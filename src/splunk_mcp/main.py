import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP
from fastapi import FastAPI

mcp_server = FastMCP("SplunkMCP")
app = FastAPI()

# Mount the FastMCP application at the /mcp path
app.mount("/mcp", mcp_server.http_app())

# Add a simple root endpoint for testing server accessibility
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@mcp_server.tool()
async def list_indexes() -> str:
    """A dummy function to test the MCP connection."""
    # Force update
    return "['test_index1', 'test_index2']"
