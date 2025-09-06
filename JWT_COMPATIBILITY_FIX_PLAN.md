# JWT Token Compatibility Fix Plan

## Problem Analysis

**Root Cause Identified**: Secret key mismatch between JWT token generation and validation.

**Issue Details**:
- `SecurityConfig` class uses `SECRET_KEY` environment variable (line 23 in security.py)
- Docker container sets `JWT_SECRET_KEY` environment variable
- Result: Security middleware generates random Fernet key instead of using JWT secret
- Token validation fails because different secret keys are used

## Solution Strategy

### 1. Fix Secret Key Configuration
Update `SecurityConfig` to use `JWT_SECRET_KEY` instead of `SECRET_KEY`:

```python
# Current (broken):
self.secret_key = os.getenv('SECRET_KEY', Fernet.generate_key())

# Fixed:
self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
```

### 2. Ensure Consistent Token Format
Verify that both generation and validation use:
- Same secret key
- Same algorithm (HS256)
- Same payload structure

### 3. Test Token Compatibility
Create comprehensive tests to verify:
- Tokens generated externally validate correctly
- Tokens work with MCP HTTP endpoints
- Authentication flow is seamless

## Implementation Steps

1. **Update Security Configuration** (Priority 1)
   - Modify `SecurityConfig.__init__()` to use `JWT_SECRET_KEY`
   - Ensure fallback to default secret key

2. **Verify Token Generation** (Priority 2)
   - Test token generation with updated configuration
   - Validate token structure and claims

3. **Test MCP Authentication** (Priority 3)
   - Test MCP tools/list with proper authentication
   - Verify JWT token validation in HTTP requests

4. **Comprehensive Testing** (Priority 4)
   - Test all MCP tools with authentication
   - Verify Splunk search functionality
   - Test ITSI operations

## Expected Outcome

After implementation:
- ✅ JWT tokens generated externally will validate correctly
- ✅ MCP HTTP endpoints will accept valid tokens
- ✅ Full MCP tool discovery and execution will work
- ✅ Splunk and ITSI operations will be accessible via MCP protocol

## Testing Strategy

1. Generate token in container
2. Test token validation locally
3. Test token with MCP HTTP endpoint
4. Test complete MCP tool execution flow
5. Verify Splunk search and ITSI operations

This fix will resolve the authentication bottleneck and enable full MCP functionality.