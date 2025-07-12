from fastmcp import FastMCP
from fastapi import FastAPI, Response
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)

# Initialize MCP with basic configuration
mcp = FastMCP("SplunkMCP")

@mcp.tool()
async def mcp_health_check() -> dict:
    return {"status": "ok", "services": ["splunk", "redis"]}

# Create main app with CORS and proper headers
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP app with proper route handling
app.mount("/mcp", mcp.http_app())

# Add explicit health endpoint with SSE support
@app.get("/health")
async def health_check(response: Response):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    return {
        "status": "ok", 
        "version": "1.0.0",
        "services": ["splunk", "redis"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8334,
        timeout_keep_alive=60,
        log_level="info"
    )
