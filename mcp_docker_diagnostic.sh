#!/bin/bash

echo "=== MCP Docker Diagnostic Tool ==="
echo "Running comprehensive checks..."

# 1. Check Docker service status
echo -e "\n[1] Docker service status:"
systemctl is-active docker

# 2. Check container status
echo -e "\n[2] Container status:"
docker ps -a

# 3. Check port binding
echo -e "\n[3] Port binding:"
docker port mcp-server

# 4. Check network configuration
echo -e "\n[4] Network configuration:"
docker network inspect mcp-network

# 5. Check container logs
echo -e "\n[5] Container logs:"
docker logs mcp-server

# 6. Test health endpoint
echo -e "\n[6] Health endpoint test:"
docker exec mcp-server curl -s http://localhost:8333/health

# 7. Test MCP endpoint
echo -e "\n[7] MCP endpoint test:"
docker exec mcp-server curl -X POST http://localhost:8333/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# 8. Resource usage
echo -e "\n[8] Resource usage:"
docker stats mcp-server --no-stream

echo -e "\n=== Diagnostic complete ==="
