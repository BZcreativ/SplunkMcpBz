import logging
from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize FastMCP with minimal configuration
mcp_server = FastMCP(
    "SplunkMCP",
    auth_required=False,
    rate_limit=None
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "mcp": "active"}

# Mount MCP server
app.mount("/mcp", mcp_server.http_app())

# Server tools
@mcp_server.tool()
async def get_server_info() -> str:
    return "SplunkMCP Server v1.0 - Production Configuration"

@mcp_server.tool()
async def list_indexes() -> list:
    return ["main", "security", "performance"]

if __name__ == "__main__":
    import uvicorn
    # Critical: Bind to 0.0.0.0 for Docker compatibility
    uvicorn.run(app, host="0.0.0.0", port=8333, log_level="info")
