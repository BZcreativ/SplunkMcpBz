# MCP Routing Fix Deployment Guide

## 🚀 Next Step: Deploy and Test the MCP Routing Fix

Now that we have the complete implementation plan and code changes, let's proceed with deploying and testing the fix.

## 📋 Deployment Checklist

### Pre-Deployment Steps:
- [ ] Review code changes in `MCP_CODE_CHANGES.md`
- [ ] Ensure you have access to the server (192.168.1.115)
- [ ] Verify GitHub repository is up to date
- [ ] Have testing commands ready

### Implementation Steps:
1. [ ] Apply code changes to main.py
2. [ ] Test locally (if possible)
3. [ ] Commit and push changes to GitHub
4. [ ] Rebuild Docker container
5. [ ] Deploy updated container
6. [ ] Run comprehensive tests

## 🔧 Step 1: Apply Code Changes

### Option A: Direct Server Update (Recommended)
SSH to the server and apply changes directly:

```bash
# SSH to the server
ssh root@192.168.1.115

# Navigate to the project directory
cd /home/toto/SplunkMcpBz

# Create a backup of current main.py
cp src/splunk_mcp/main.py src/splunk_mcp/main.py.backup.$(date +%Y%m%d_%H%M%S)

# Apply the changes (you'll need to manually edit or use a script)
# The changes are detailed in MCP_CODE_CHANGES.md
```

### Option B: Local Development First
Make changes locally, test, then deploy:

```bash
# On your local machine
cd SplunkMcpBz

# Backup current main.py
cp src/splunk_mcp/main.py src/splunk_mcp/main.py.backup

# Apply changes from MCP_CODE_CHANGES.md
# Then test locally before pushing
```

## 🧪 Step 2: Test the Implementation

### Test Script Creation
Create this test script on the server:

```bash
# Create test script
cat > test_mcp_routing.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing MCP Routing Fix"
echo "========================="

# Configuration
MCP_HOST="192.168.1.115"
MCP_PORT="8334"
BASE_URL="http://${MCP_HOST}:${MCP_PORT}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_pattern="$3"
    
    echo -n "Testing: $test_name... "
    
    if result=$(eval "$command" 2>/dev/null); then
        if echo "$result" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✅ PASSED${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAILED${NC}"
            echo "Expected: $expected_pattern"
            echo "Got: $result"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Command execution failed"
        ((TESTS_FAILED++))
    fi
}

# Get authentication token
echo "🔑 Getting authentication token..."
TOKEN=$(curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o "\"access_token\":\"[^\"]*" | cut -d"\"" -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get authentication token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Got authentication token${NC}"

# Test 1: MCP Tool Discovery
run_test "MCP Tool Discovery" \
  "curl -s -H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' -X POST ${BASE_URL}/mcp/ -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/list\",\"params\":{},\"id\":1}'" \
  "tools"

# Test 2: MCP Health Check Tool
run_test "MCP Health Check Tool" \
  "curl -s -H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' -X POST ${BASE_URL}/mcp/ -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"mcp_health_check\",\"arguments\":{}},\"id\":2}'" \
  "content"

# Test 3: List Indexes Tool
run_test "List Indexes Tool" \
  "curl -s -H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' -X POST ${BASE_URL}/mcp/ -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"list_indexes\",\"arguments\":{}},\"id\":3}'" \
  "content"

# Test 4: Splunk Search Tool
run_test "Splunk Search Tool" \
  "curl -s -H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' -X POST ${BASE_URL}/mcp/ -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"splunk_search\",\"arguments\":{\"query\":\"search index=_internal | head 1\",\"earliest_time\":\"-1h\",\"latest_time\":\"now\"}},\"id\":4}'" \
  "content"

# Test 5: ITSI Services Tool
run_test "ITSI Services Tool" \
  "curl -s -H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' -X POST ${BASE_URL}/mcp/ -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"get_itsi_services\",\"arguments\":{}},\"id\":5}'" \
  "content"

# Summary
echo ""
echo "========================="
echo "🏁 Test Summary:"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! MCP routing is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the server logs.${NC}"
    echo "Check logs with: docker logs splunk-mcp-test --tail 50"
    exit 1
fi
EOF

chmod +x test_mcp_routing.sh
```

## 🚀 Step 3: Deploy and Test

### Deploy the Updated Code
```bash
# SSH to server and apply changes
ssh root@192.168.1.115

# Navigate to project directory
cd /home/toto/SplunkMcpBz

# Apply the code changes (you'll need to edit main.py manually or use a script)
# The changes are detailed in MCP_CODE_CHANGES.md

# After applying changes, rebuild the container
docker stop splunk-mcp-test
docker rm splunk-mcp-test
docker build --no-cache -t splunk-mcp-fixed .
docker run -d --name splunk-mcp-test -p 8334:8334 \
  -e SPLUNK_HOST=192.168.1.15 \
  -e SPLUNK_PORT=8089 \
  -e SPLUNK_SCHEME=https \
  -e SPLUNK_TOKEN=6eef93338c577e41fd229743056909c6d118d289d131fc36119976fa5c1edcbf \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6379 \
  -e JWT_SECRET_KEY=your-secret-key-here \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=admin123 \
  --restart unless-stopped \
  splunk-mcp-fixed
```

### Run the Test Suite
```bash
# Execute the test script
./test_mcp_routing.sh

# Monitor logs during testing
docker logs -f splunk-mcp-test
```

## 📊 Validation Checklist

### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] Health endpoint responds correctly
- [ ] Authentication works properly

### ✅ MCP Protocol Compliance
- [ ] `/mcp/` endpoint responds to POST requests
- [ ] JSON-RPC 2.0 format is supported
- [ ] Tool discovery returns available tools
- [ ] Tool execution works correctly

### ✅ Tool-Specific Tests
- [ ] `mcp_health_check` tool executes successfully
- [ ] `list_indexes` tool returns Splunk indexes
- [ ] `splunk_search` tool executes searches
- [ ] `get_itsi_services` tool returns ITSI services

### ✅ Error Handling
- [ ] Invalid JSON returns proper error
- [ ] Missing authentication returns 401
- [ ] Invalid token returns proper error
- [ ] Tool execution errors are handled gracefully

## 🚨 Troubleshooting

If tests fail:

1. **Check Container Logs**:
   ```bash
   docker logs splunk-mcp-test --tail 50
   ```

2. **Verify Code Changes**:
   ```bash
   docker exec splunk-mcp-test cat /app/src/splunk_mcp/main.py | head -50
   ```

3. **Test Individual Components**:
   ```bash
   # Test health
   curl -s http://192.168.1.115:8334/api/health
   
   # Test auth
   curl -s -X POST http://192.168.1.115:8334/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

4. **Check Network Connectivity**:
   ```bash
   curl -s http://192.168.1.115:8334/api/health
   ```

## 📈 Performance Targets

- **Response Time**: < 500ms for tool discovery
- **Response Time**: < 2s for tool execution
- **Success Rate**: > 95% for all operations
- **Error Rate**: < 5% under normal load

## 🎯 Next Steps After Successful Testing

1. **Performance Testing**: Run load tests
2. **Security Validation**: Complete security audit
3. **Documentation Update**: Update all documentation
4. **Production Deployment**: Deploy to production environment
5. **Monitoring Setup**: Configure monitoring and alerting

This deployment guide provides a systematic approach to implementing and testing the MCP routing fix.