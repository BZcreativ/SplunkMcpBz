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

import os
from fastapi import HTTPException

# Initialize FastMCP with default configuration
try:
    mcp_server = FastMCP("SplunkMCP")
except Exception as e:
    logger.error(f"Failed to initialize MCP server: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Failed to initialize MCP server components"
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "mcp": "active"}

# Mount MCP server with versioned path
app.mount("/api/v1/mcp", mcp_server.http_app())

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
