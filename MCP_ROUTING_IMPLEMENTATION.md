# MCP HTTP Routing Implementation Plan

## 🎯 Objective
Fix the MCP HTTP routing to make tools accessible through standard MCP protocol endpoints.

## 🔍 Current Issue Analysis

Based on testing, we identified:
- MCP tools are registered successfully (visible in logs)
- Authentication works correctly
- Health endpoints respond properly
- But `/mcp/` endpoint returns "Not Found"

## 🛠️ Solution Architecture

### 1. MCP Protocol Requirements
The MCP protocol expects:
- **Endpoint**: `POST /mcp/`
- **Headers**: `Content-Type: application/json`, `Authorization: Bearer <token>`
- **Body**: JSON-RPC 2.0 format
- **Methods**: `tools/list`, `tools/call`, etc.

### 2. Required Implementation

#### A. Create MCP HTTP Handler
We need to add a proper MCP HTTP handler that:
1. Accepts JSON-RPC 2.0 requests
2. Authenticates requests
3. Routes to appropriate MCP tools
4. Returns proper JSON-RPC responses

#### B. Integration Points
- Integrate with existing authentication system
- Use existing MCP tool registry
- Maintain current security model
- Preserve all existing functionality

## 📋 Implementation Steps

### Step 1: Add MCP HTTP Handler to main.py

Add this code to the main.py file after the existing MCP tool definitions:

```python
# MCP HTTP Handler - Add after existing MCP tool definitions
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
    for tool_name, tool_info in mcp._tools.items():
        # Check if user has permission for this tool
        if tool_name == "list_indexes" and not check_permission('read:search'):
            continue
        elif tool_name == "splunk_search" and not check_permission('read:search'):
            continue
        elif tool_name.startswith("get_itsi_") and not check_permission('read:itsi'):
            continue
        
        tools.append({
            "name": tool_name,
            "description": tool_info.get("description", ""),
            "inputSchema": {
                "type": "object",
                "properties": {},  # Add parameter schema based on tool signature
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
        result = await mcp.call_tool(tool_name, tool_args)
        
        # Format result according to MCP specification
        if isinstance(result, (list, dict)):
            content = [{"type": "text", "text": json.dumps(result)}]
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

### Step 2: Update Imports and Dependencies

Add these imports at the top of main.py:
```python
import json
from fastapi.responses import JSONResponse
```

### Step 3: Fix Authentication Integration

Update the authentication middleware to properly handle the user context:
```python
# Update the set_current_user function to be more robust
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

### Step 4: Test the Implementation

Create test commands to verify the fix:
```bash
# Test tool discovery
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8334/mcp/ \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# Test tool execution
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8334/mcp/ \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"mcp_health_check","arguments":{}},"id":2}'
```

## 🔍 Key Changes Required

1. **Replace Custom ASGI Handler**: The current complex ASGI routing needs to be replaced with proper FastAPI endpoints
2. **Add JSON-RPC Support**: Implement proper JSON-RPC 2.0 parsing and response formatting
3. **Fix Authentication Flow**: Ensure authentication works correctly with the new endpoint structure
4. **Tool Result Formatting**: Format tool results according to MCP specification

## 🎯 Expected Outcome

After implementation:
- ✅ `/mcp/` endpoint will respond to POST requests
- ✅ JSON-RPC 2.0 format will be properly supported
- ✅ All MCP tools will be discoverable via `tools/list`
- ✅ All MCP tools will be executable via `tools/call`
- ✅ Authentication will work seamlessly
- ✅ Error handling will follow MCP specifications

This implementation will resolve the "Not Found" issue and make the MCP tools fully accessible through standard MCP protocol endpoints.