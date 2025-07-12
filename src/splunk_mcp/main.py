print("SPLUNK MCP SERVER STARTING")  # Module-level print to verify execution
from fastmcp import FastMCP
from fastapi import FastAPI, Response
import logging
from fastapi.middleware.cors import CORSMiddleware

# Initialize logging first
print("Initializing logging configuration")  # Will show in container logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Start with just console logging
    ]
)
logger = logging.getLogger('mcp.protocol')
logger.info("Logger successfully initialized")

# Initialize MCP with basic configuration
mcp = FastMCP("SplunkMCP")
logger.info("MCP initialized")

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

# Mount MCP app at /mcp to avoid route conflicts
app.mount("/mcp", mcp.http_app())
logger.info("MCP routes mounted at /mcp")

# Add explicit health endpoint with SSE support
@app.get("/api/health")
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
        log_config=None  # Use our existing logging config
    )
