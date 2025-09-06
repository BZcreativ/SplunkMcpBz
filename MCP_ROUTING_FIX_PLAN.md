# MCP HTTP Routing Fix Plan

## 🎯 Problem Statement

The MCP tools are properly registered at the server level but are not accessible through standard HTTP endpoints. The `/mcp/` endpoint returns "Not Found" when attempting to access MCP tools.

## 🔍 Current Status Analysis

### ✅ What's Working:
- MCP server initializes successfully
- All MCP tools are registered (visible in logs)
- Authentication system works
- Health endpoints respond correctly
- Tools are defined with `@mcp.tool()` decorators

### ❌ What's Broken:
- HTTP endpoint `/mcp/` returns "Not Found"
- MCP protocol JSON-RPC requests fail
- Tools not accessible through standard MCP interface

## 🕵️ Root Cause Investigation

### 1. Current Routing Architecture
```
FastAPI App
├── /api/health (✅ Working)
├── /api/auth/* (✅ Working)
└── /mcp/* (❌ Not Working)
    └── Custom MCP Router (Problem Area)
```

### 2. MCP Protocol Requirements
The MCP protocol expects:
- **Endpoint**: `/mcp/` or `/mcp`
- **Method**: POST
- **Content-Type**: application/json
- **Body**: JSON-RPC 2.0 format
- **Authentication**: Bearer token in header

### 3. Expected JSON-RPC Format
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 1
}
```

## 🛠️ Solution Design

### Option 1: Direct MCP Integration (Recommended)
Replace the custom MCP router with proper FastMCP HTTP integration.

### Option 2: Custom JSON-RPC Handler
Create a dedicated endpoint that properly handles MCP JSON-RPC requests.

### Option 3: FastAPI-MCP Bridge
Implement a bridge that translates between FastAPI and MCP protocols.

## 📋 Implementation Plan

### Phase 1: Analysis & Design (Current)
- [x] Identify routing issue
- [x] Analyze current implementation
- [x] Research MCP protocol specifications
- [ ] Design proper endpoint structure
- [ ] Plan authentication integration

### Phase 2: Implementation
- [ ] Create MCP-compliant HTTP handler
- [ ] Integrate with existing authentication
- [ ] Implement proper JSON-RPC parsing
- [ ] Add error handling and validation

### Phase 3: Testing & Validation
- [ ] Test tool discovery (tools/list)
- [ ] Test tool execution (tools/call)
- [ ] Test authentication integration
- [ ] Test error scenarios
- [ ] Performance validation

## 🔧 Technical Implementation Details

### 1. MCP Endpoint Structure
```
POST /mcp/
Headers:
  Content-Type: application/json
  Authorization: Bearer <token>

Body:
{
  "jsonrpc": "2.0",
  "method": "tools/list"|"tools/call",
  "params": {...},
  "id": <request_id>
}
```

### 2. Required Endpoints
- `tools/list` - Discover available tools
- `tools/call` - Execute specific tools
- `resources/list` - List available resources
- `prompts/list` - List available prompts

### 3. Response Format
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [...],
    "content": [...]
  },
  "id": <request_id>
}
```

## 🚀 Implementation Steps

### Step 1: Create MCP HTTP Handler
```python
@mcp_router.post("/")
async def handle_mcp_request(request: Request):
    """Handle MCP JSON-RPC requests"""
    try:
        # Parse JSON-RPC request
        body = await request.json()
        
        # Validate JSON-RPC format
        if body.get("jsonrpc") != "2.0":
            return {"error": {"code": -32600, "message": "Invalid Request"}}
        
        # Route to appropriate handler
        method = body.get("method")
        params = body.get("params", {})
        
        if method == "tools/list":
            return await handle_tools_list(request)
        elif method == "tools/call":
            return await handle_tools_call(request, params)
        # ... other methods
        
    except Exception as e:
        return {"error": {"code": -32603, "message": str(e)}}
```

### Step 2: Tool Discovery Handler
```python
async def handle_tools_list(request: Request):
    """Handle tools/list request"""
    # Get authenticated user
    user_data = await get_authenticated_user(request)
    
    # Get list of available tools
    tools = []
    for tool_name, tool_func in mcp._tools.items():
        tools.append({
            "name": tool_name,
            "description": tool_func.__doc__ or "",
            "inputSchema": {
                "type": "object",
                "properties": {},  # Add parameter schema
                "required": []
            }
        })
    
    return {
        "jsonrpc": "2.0",
        "result": {"tools": tools},
        "id": request.json().get("id")
    }
```

### Step 3: Tool Execution Handler
```python
async def handle_tools_call(request: Request, params: dict):
    """Handle tools/call request"""
    # Get authenticated user
    user_data = await get_authenticated_user(request)
    
    # Extract tool name and arguments
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})
    
    # Set user context for authorization
    set_current_user(user_data)
    
    try:
        # Execute the tool
        result = await mcp.call_tool(tool_name, tool_args)
        
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": str(result)}]},
            "id": request.json().get("id")
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": request.json().get("id")
        }
```

## 🧪 Testing Strategy

### 1. Unit Tests
- Test JSON-RPC parsing
- Test authentication integration
- Test tool discovery
- Test tool execution

### 2. Integration Tests
- Test complete request/response cycle
- Test authentication flow
- Test error handling
- Test concurrent requests

### 3. Protocol Compliance Tests
- Validate JSON-RPC 2.0 format
- Test proper error codes
- Test request/response correlation
- Test batch request handling

## 📊 Success Criteria

### ✅ Must Have:
- [ ] `/mcp/` endpoint responds to POST requests
- [ ] Proper JSON-RPC 2.0 format support
- [ ] Authentication integration works
- [ ] Tool discovery returns correct tool list
- [ ] Tool execution calls actual MCP functions
- [ ] Error responses follow MCP specification

### 🎯 Nice to Have:
- [ ] Batch request support
- [ ] Request validation and sanitization
- [ ] Performance optimization
- [ ] Detailed logging and monitoring
- [ ] Rate limiting and throttling

## 🚀 Next Steps

1. **Analyze Current Code**: Examine the existing MCP router implementation
2. **Design New Architecture**: Create proper MCP HTTP handler
3. **Implement Solution**: Code the routing fix
4. **Test Thoroughly**: Validate all functionality
5. **Deploy and Verify**: Test in production environment

This plan provides a systematic approach to resolving the MCP HTTP routing issue and making the tools accessible through standard MCP protocol endpoints.