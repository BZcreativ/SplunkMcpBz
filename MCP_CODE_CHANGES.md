# MCP HTTP Routing Code Changes

## 🎯 Objective
Implement the actual code changes needed to fix the MCP HTTP routing issue.

## 📝 Changes Required in main.py

### Step 1: Add Required Imports
Add these imports at the top of `main.py`:

```python
import json
from fastapi.responses import JSONResponse
```

### Step 2: Replace the Current MCP Router
Find the current `mcp_router` implementation (around lines 790-870) and replace it with this:

```python
# MCP HTTP Handler - JSON-RPC 2.0 Compliant
@mcp_router.post("/")
async def handle_mcp_request(request: Request):
    """Handle MCP JSON-RPC requests"""
    try:
        # Parse JSON-RPC request
        body = await request.json()
        
        # Validate JSON-RPC format
        if body.get("jsonrpc") != "2.0":
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": body.get("id", None)
                }
            )
        
        # Get authenticated user from token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": "Authentication required"},
                    "id": body.get("id", None)
                }
            )
        
        token = auth_header.split(" ")[1]
        user_data = security_middleware.authenticate_request(token)
        
        if not user_data:
            return JSONResponse(
                status_code=401,
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": "Invalid token"},
                    "id": body.get("id", None)
                }
            )
        
        # Set user context for authorization
        set_current_user(user_data)
        
        # Route to appropriate handler
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "tools/list":
            result = await handle_tools_list(user_data)
        elif method == "tools/call":
            result = await handle_tools_call(user_data, params)
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                }
            )
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        )
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            }
        )
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error"},
                "id": body.get("id", None) if 'body' in locals() else None
            }
        )

async def handle_tools_list(user_data: Dict[str, Any]) -> dict:
    """Handle tools/list request"""
    tools = []
    
    # Get all registered MCP tools
    for tool_name in mcp._tools.keys():
        # Check if user has permission for this tool
        if tool_name == "list_indexes" and not check_permission('read:search'):
            continue
        elif tool_name == "splunk_search" and not check_permission('read:search'):
            continue
        elif tool_name.startswith("get_itsi_") and not check_permission('read:itsi'):
            continue
        
        # Get tool function for description
        tool_func = globals().get(tool_name)
        description = tool_func.__doc__ if tool_func else ""
        
        tools.append({
            "name": tool_name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": {},  # Simplified for now
                "required": []
            }
        })
    
    return {"tools": tools}

async def handle_tools_call(user_data: Dict[str, Any], params: dict) -> dict:
    """Handle tools/call request"""
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})
    
    if not tool_name:
        raise ValueError("Tool name is required")
    
    # Check permission for the specific tool
    if tool_name == "list_indexes" and not check_permission('read:search'):
        raise PermissionError("Insufficient permissions for list_indexes")
    elif tool_name == "splunk_search" and not check_permission('read:search'):
        raise PermissionError("Insufficient permissions for splunk_search")
    elif tool_name.startswith("get_itsi_") and not check_permission('read:itsi'):
        raise PermissionError("Insufficient permissions for ITSI operations")
    
    # Execute the tool
    try:
        # Get the tool function
        tool_func = globals().get(tool_name)
        if not tool_func:
            raise ValueError(f"Tool {tool_name} not found")
        
        # Execute with proper arguments
        if tool_name in ["splunk_search"]:
            result = await tool_func(
                query=tool_args.get("query", "*"),
                earliest_time=tool_args.get("earliest_time", "-24h"),
                latest_time=tool_args.get("latest_time", "now"),
                output_mode=tool_args.get("output_mode", "json"),
                use_cache=tool_args.get("use_cache", True)
            )
        elif tool_name in ["get_itsi_services", "get_itsi_kpis", "get_itsi_alerts"]:
            result = await tool_func(
                service_name=tool_args.get("service_name")
            )
        elif tool_name in ["get_itsi_service_health"]:
            result = await tool_func(
                service_name=tool_args.get("service_name", "")
            )
        else:
            # For tools without parameters
            result = await tool_func()
        
        # Format result according to MCP specification
        if isinstance(result, (list, dict)):
            content = [{"type": "text", "text": json.dumps(result, default=str)}]
        else:
            content = [{"type": "text", "text": str(result)}]
        
        return {"content": content}
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise RuntimeError(f"Tool execution failed: {str(e)}")

# Helper function to get authenticated user from request
async def get_authenticated_user(request: Request) -> Dict[str, Any]:
    """Extract and validate authenticated user from request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")
    
    token = auth_header.split(" ")[1]
    user_data = security_middleware.authenticate_request(token)
    
    if not user_data:
        raise ValueError("Invalid or expired token")
    
    return user_data
```

### Step 3: Fix the Authentication Context Issue
Update the `get_current_user_info` function to handle the authentication properly:

```python
@api_router.get("/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Get current user information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    return {
        "user_id": current_user['user_id'],
        "username": current_user['username'],
        "roles": current_user['roles'],
        "permissions": security_middleware.rbac.get_user_permissions(current_user['roles'])
    }
```

### Step 4: Update the User Context Management
Ensure the user context functions work properly:

```python
# Update set_current_user to be more robust
def set_current_user(user_data: Dict[str, Any]):
    """Set the current user context for MCP tools"""
    global current_user_context
    current_user_context = user_data
    logger.info(f"User context set: {user_data.get('user_id', 'unknown')}")

# Update check_permission to handle None user
def check_permission(permission: str) -> bool:
    """Check if current user has required permission"""
    user_data = get_current_user_context()
    if not user_data:
        logger.warning("No user context available for permission check")
        return False
    return security_middleware.authorize_request(user_data, permission)
```

## 🧪 Testing Commands

After implementing these changes, test with:

```bash
# Get authentication token
TOKEN=$(curl -s -X POST http://192.168.1.115:8334/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o "\"access_token\":\"[^\"]*" | cut -d"\"" -f4)

# Test tool discovery
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST http://192.168.1.115:8334/mcp/ \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# Test tool execution
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST http://192.168.1.115:8334/mcp/ \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"mcp_health_check","arguments":{}},"id":2}'

# Test Splunk search
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST http://192.168.1.115:8334/mcp/ \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_indexes","arguments":{}},"id":3}'
```

## 🚀 Deployment Steps

1. **Apply Changes**: Update the `main.py` file with the code above
2. **Test Locally**: Verify changes work in development environment
3. **Commit Changes**: Push updated code to GitHub repository
4. **Rebuild Container**: Build new Docker image with changes
5. **Deploy**: Deploy updated container to production
6. **Validate**: Run comprehensive tests to confirm fix

## ✅ Success Criteria

After implementation, verify:
- [ ] `/mcp/` endpoint responds with 200 status
- [ ] `tools/list` returns available tools
- [ ] `tools/call` executes tools successfully
- [ ] Authentication works correctly
- [ ] Error handling follows MCP specification
- [ ] All existing functionality remains intact

This implementation will resolve the "Not Found" issue and make the MCP tools fully accessible through standard MCP protocol endpoints.