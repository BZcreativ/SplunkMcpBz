import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a standard FastAPI application
app = FastAPI()

# Apply comprehensive CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the FastMCP server on the FastAPI app
mcp_server = FastMCP("SplunkMCP")
app.mount("/mcp", mcp_server.http_app())

@mcp_server.tool()
async def get_server_info() -> str:
    """Get basic server information."""
    return "SplunkMCP Server v1.0 - Standalone FastMCP Implementation"

@mcp_server.tool()
async def list_indexes() -> list:
    """List all Splunk indexes."""
    # Actual implementation will go here
    return ["main", "security", "performance"]

@mcp_server.tool()
async def search(query: str) -> dict:
    """Perform a Splunk search."""
    # Actual implementation will go here
    return {"job_id": "12345", "status": "running"}

@mcp_server.tool()
async def get_job_status(job_id: str) -> dict:
    """Get the status of a Splunk search job."""
    # Actual implementation will go here
    return {"job_id": job_id, "status": "completed"}

@mcp_server.tool()
async def get_job_results(job_id: str) -> list:
    """Get the results of a Splunk search job."""
    # Actual implementation will go here
    return [{"event": "sample event data"}]

# Run the server directly without FastAPI
if __name__ == "__main__":
    import uvicorn
    # Run the main FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8333)
