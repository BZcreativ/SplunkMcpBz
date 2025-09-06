#!/bin/bash
# Deployment script for fixed Splunk MCP Server

set -e

echo "🚀 Deploying Fixed Splunk MCP Server..."
echo "======================================"

# Configuration
REMOTE_HOST="192.168.1.115"
REMOTE_USER="root"
CONTAINER_NAME="splunk-mcp-test"
IMAGE_NAME="splunk-mcp-fixed"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we can connect to remote server
log_info "Testing connection to remote server..."
if ! ssh -o ConnectTimeout=5 ${REMOTE_USER}@${REMOTE_HOST} "echo 'Connection test successful'"; then
    log_error "Cannot connect to remote server ${REMOTE_HOST}"
    exit 1
fi

# Copy the fixed main.py to remote server
log_info "Copying fixed MCP server code to remote server..."
scp src/splunk_mcp/main_fixed.py ${REMOTE_USER}@${REMOTE_HOST}:/tmp/main_fixed.py

# Create backup of original and replace with fixed version
log_info "Creating backup and deploying fixed version..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    set -e
    
    # Stop the current container
    echo "Stopping current MCP server container..."
    docker stop splunk-mcp-test || true
    docker rm splunk-mcp-test || true
    
    # Backup original main.py
    if [ -f /home/toto/splunk-mcp/src/splunk_mcp/main.py ]; then
        cp /home/toto/splunk-mcp/src/splunk_mcp/main.py /home/toto/splunk-mcp/src/splunk_mcp/main.py.backup
        echo "Original main.py backed up to main.py.backup"
    fi
    
    # Copy fixed version
    cp /tmp/main_fixed.py /home/toto/splunk-mcp/src/splunk_mcp/main.py
    chown toto:toto /home/toto/splunk-mcp/src/splunk_mcp/main.py
    
    # Navigate to project directory
    cd /home/toto/splunk-mcp
    
    # Build new Docker image with fixed code
    echo "Building new Docker image with fixed MCP server..."
    docker build -t splunk-mcp-fixed .
    
    # Run the fixed container
    echo "Starting fixed MCP server container..."
    docker run -d \
        --name splunk-mcp-test \
        -p 8334:8334 \
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
    
    echo "Waiting for server to start..."
    sleep 10
    
    # Test the connection
    echo "Testing MCP server health..."
    if curl -s http://localhost:8334/api/health | grep -q "ok"; then
        echo "✅ MCP server is running and healthy!"
    else
        echo "❌ MCP server health check failed"
        exit 1
    fi
    
    echo "✅ Fixed MCP server deployed successfully!"
ENDSSH

log_info "Deployment completed successfully!"
log_info "Testing MCP tools availability..."

# Test the MCP tools
sleep 5
log_info "Testing MCP tools..."

# Get authentication token
TOKEN_RESPONSE=$(curl -s -X POST http://${REMOTE_HOST}:8334/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    log_info "Authentication successful, testing MCP tools..."
    
    # Test list_indexes tool
    log_info "Testing list_indexes tool..."
    INDEXES_RESULT=$(curl -s -H "Authorization: Bearer $TOKEN" http://${REMOTE_HOST}:8334/mcp/list_indexes)
    if echo "$INDEXES_RESULT" | grep -q "\["; then
        log_info "✅ list_indexes tool is working!"
    else
        log_warn "⚠️  list_indexes tool may have issues"
    fi
    
    # Test health check tool
    log_info "Testing mcp_health_check tool..."
    HEALTH_RESULT=$(curl -s -H "Authorization: Bearer $TOKEN" http://${REMOTE_HOST}:8334/mcp/mcp_health_check)
    if echo "$HEALTH_RESULT" | grep -q "ok"; then
        log_info "✅ mcp_health_check tool is working!"
    else
        log_warn "⚠️  mcp_health_check tool may have issues"
    fi
    
    log_info "✅ MCP tools are now available for Roo Code integration!"
else
    log_error "Failed to authenticate with MCP server"
    exit 1
fi

log_info "🎉 Deployment and testing completed successfully!"
log_info "The Splunk MCP server is now ready for use with Roo Code."