import sys
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create FastAPI app
app = FastAPI()

# Minimal CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom WebSocket protocol with origin bypass
class AllowAllWebSocket(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        kwargs['origins'] = None  # Disable origin validation
        super().__init__(*args, **kwargs)

# Configure FastMCP server with debug logging
logger.info("Initializing FastMCP server...")
mcp_server = FastMCP(
    "SplunkMCP",
    websocket_class=AllowAllWebSocket,
    allowed_origins=["*"],
    auth_required=False,
    rate_limit=None
)
logger.info(f"FastMCP server configured with: {mcp_server.config}")

# Mount MCP server
app.mount("/mcp", mcp_server.http_app())
logger.info("Mounted FastMCP server at /mcp")

# Server tools
@mcp_server.tool()
async def get_server_info() -> str:
    return "SplunkMCP Server v1.0 - Standalone FastMCP Implementation"

@mcp_server.tool()
async def list_indexes() -> list:
    return ["main", "security", "performance"]

@mcp_server.tool()
async def search(query: str) -> dict:
    return {"job_id": "12345", "status": "running"}

@mcp_server.tool()
async def get_job_status(job_id: str) -> dict:
    return {"job_id": job_id, "status": "completed"}

@mcp_server.tool()
async def get_job_results(job_id: str) -> list:
    return [{"event": "sample event data"}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8333)
