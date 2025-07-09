import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP

# Create a standalone FastMCP server
mcp_server = FastMCP("SplunkMCP")

@mcp_server.tool()
async def list_indexes() -> str:
    """A dummy function to test the MCP connection."""
    return "['test_index1', 'test_index2']"

@mcp_server.tool()
async def get_server_info() -> str:
    """Get basic server information."""
    return "SplunkMCP Server v1.0 - Standalone FastMCP Implementation"

# Run the server directly without FastAPI
if __name__ == "__main__":
    import uvicorn
    # Use FastMCP's built-in HTTP server
    uvicorn.run(mcp_server.http_app(), host="0.0.0.0", port=8333)
