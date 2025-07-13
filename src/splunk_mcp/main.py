print("SPLUNK MCP SERVER STARTING")  # Module-level print to verify execution
from fastmcp import FastMCP
from fastapi import FastAPI, Response, Request
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

@mcp.tool()
async def list_indexes() -> list:
    """List all Splunk indexes"""
    import splunklib.client as client
    import os
    
    try:
        service = client.connect(
            host=os.getenv("SPLUNK_HOST", "localhost"),
            port=int(os.getenv("SPLUNK_PORT", "8089")),
            splunkToken=os.getenv("SPLUNK_TOKEN"),
            scheme=os.getenv("SPLUNK_SCHEME", "https")
        )
        return [idx.name for idx in service.indexes]
    except Exception as e:
        logger.error(f"Failed to list indexes: {str(e)}")
        raise

# Create main app with CORS and proper headers
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*", "MCP-Protocol-Version", "Mcp-Session-Id"],
    expose_headers=["MCP-Protocol-Version", "Mcp-Session-Id"]
)

# Mount MCP app at /mcp to avoid route conflicts
app.mount("/mcp", mcp.http_app())
app.mount("/mcp/", mcp.http_app())  # Handle trailing slash
logger.info("MCP routes mounted at /mcp and /mcp/")

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

# MCP Standard HTTP Transport Endpoints
@app.post("/api/mcp")
async def handle_mcp_post(request: Request):
    """Handle MCP JSON-RPC messages via POST"""
    async def send_wrapper(message, send):
        if message["type"] == "http.response.start":
            message["headers"].append((b"MCP-Protocol-Version", b"2025-06-18"))
            message["headers"].append((b"Cache-Control", b"no-cache"))
        return await send(message)
    
    return await mcp.http_app()(request.scope, request.receive, lambda msg: send_wrapper(msg, request._send))

@app.get("/api/mcp")
async def handle_mcp_get(request: Request):
    """Handle MCP SSE stream via GET"""
    async def send_wrapper(message, send):
        if message["type"] == "http.response.start":
            message["headers"].append((b"MCP-Protocol-Version", b"2025-06-18"))
            message["headers"].append((b"Cache-Control", b"no-cache"))
        return await send(message)
    
    return await mcp.http_app()(request.scope, request.receive, lambda msg: send_wrapper(msg, request._send))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8334,
        timeout_keep_alive=60,
        log_config=None  # Use our existing logging config
    )
