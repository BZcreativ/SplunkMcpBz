print("SPLUNK MCP SERVER STARTING")  # Module-level print to verify execution
from fastmcp import FastMCP
from fastapi import FastAPI, Response, Request
import logging
import os
from fastapi.middleware.cors import CORSMiddleware

# Custom exceptions
class SplunkConnectionError(Exception):
    """Raised when connection to Splunk fails"""
    pass

class SplunkQueryError(Exception):
    """Raised when a Splunk query fails"""
    pass

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

def get_splunk_service(max_retries: int = 3):
    """Get Splunk service connection with retry logic"""
    import splunklib.client as client
    import os
    import time
    
    last_error = None
    for attempt in range(max_retries):
        metrics.increment_connection_attempts()
        try:
            host = os.getenv("SPLUNK_HOST", "localhost")
            port = int(os.getenv("SPLUNK_PORT", "8089"))
            scheme = os.getenv("SPLUNK_SCHEME", "https")
            token = os.getenv("SPLUNK_TOKEN")
            
            logger.debug(f"Attempting Splunk connection to {scheme}://{host}:{port}")
            logger.debug(f"Using token: {'*****' if token else 'NOT SET'}")
            
            service = client.connect(
                host=host,
                port=port,
                splunkToken=token,
                scheme=scheme
            )
            metrics.increment_connection_successes()
            return service
        except Exception as e:
            last_error = e
            metrics.increment_connection_failures()
            logger.warning(f"Splunk connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    raise SplunkConnectionError(f"Failed to connect to Splunk after {max_retries} attempts: {str(last_error)}")

# Monitoring metrics
class SplunkMetrics:
    def __init__(self):
        self.connection_attempts = 0
        self.connection_successes = 0
        self.connection_failures = 0
        self.query_count = 0
        self.query_errors = 0
        self.query_timeouts = 0

    def increment_connection_attempts(self):
        self.connection_attempts += 1

    def increment_connection_successes(self):
        self.connection_successes += 1

    def increment_connection_failures(self):
        self.connection_failures += 1

    def increment_query_count(self):
        self.query_count += 1

    def increment_query_errors(self):
        self.query_errors += 1

    def increment_query_timeouts(self):
        self.query_timeouts += 1

    def get_metrics(self):
        return {
            "connections": {
                "attempts": self.connection_attempts,
                "successes": self.connection_successes,
                "failures": self.connection_failures,
                "success_rate": self.connection_successes / max(1, self.connection_attempts)
            },
            "queries": {
                "count": self.query_count,
                "errors": self.query_errors,
                "timeouts": self.query_timeouts,
                "error_rate": self.query_errors / max(1, self.query_count)
            }
        }

metrics = SplunkMetrics()

# Initialize MCP with basic configuration
mcp = FastMCP("SplunkMCP")
logger.info("MCP initialized")

@mcp.tool()
async def mcp_health_check() -> dict:
    return {"status": "ok", "services": ["splunk", "redis"]}

@mcp.tool()
async def list_indexes() -> list:
    """List all Splunk indexes"""
    try:
        service = get_splunk_service()
        indexes = service.indexes
        if not indexes:
            logger.warning("No indexes found in Splunk")
            return []
        return [idx.name for idx in indexes]
    except SplunkConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing indexes: {str(e)}")
        raise SplunkQueryError("Failed to list indexes") from e

@mcp.tool()
async def search_splunk(query: str, index: str = "*", earliest: str = "-24h", latest: str = "now") -> dict:
    """Search Splunk data using SPL query"""
    metrics.increment_query_count()
    try:
        service = get_splunk_service()
        
        if not query.strip():
            metrics.increment_query_errors()
            raise SplunkQueryError("Empty query provided")
            
        kwargs = {
            "search_mode": "normal",
            "earliest_time": earliest,
            "latest_time": latest,
            "index": index
        }
        
        search_query = f"search {query}"
        job = service.jobs.create(search_query, **kwargs)
        
        # Wait for completion with timeout
        timeout = 30  # seconds
        start_time = time.time()
        while not job.is_done():
            if time.time() - start_time > timeout:
                metrics.increment_query_timeouts()
                job.cancel()
                raise SplunkQueryError(f"Query timed out after {timeout} seconds")
            job.refresh()
            await asyncio.sleep(0.5)
            
        results = list(job.results())
        if not results:
            return {"status": "completed", "message": "No results found"}
            
        return {
            "results": [dict(r) for r in results],
            "summary": job["content"]["messages"],
            "status": job["content"]["dispatchState"]
        }
    except SplunkConnectionError as e:
        metrics.increment_query_errors()
        logger.error(f"Connection error: {str(e)}")
        raise
    except SplunkQueryError as e:
        metrics.increment_query_errors()
        logger.error(f"Query error: {str(e)}")
        raise
    except Exception as e:
        metrics.increment_query_errors()
        logger.error(f"Unexpected search error: {str(e)}")
        raise SplunkQueryError("Search failed") from e

# Create main app with CORS and proper headers
app = FastAPI()

# Add API routes first
@app.get("/api/metrics")
async def get_metrics(response: Response):
    """Get current server metrics"""
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["MCP-Protocol-Version"] = "2025-06-18"
    return metrics.get_metrics()

@app.get("/api/health")
async def health_check(response: Response):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    return {
        "status": "ok", 
        "version": "1.0.0",
        "services": ["splunk", "redis"]
    }

@app.get("/api/test-splunk-connection")
async def test_splunk_connection(response: Response):
    """Test Splunk connection with current token"""
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    try:
        service = get_splunk_service()
        return {
            "status": "success",
            "message": "Successfully connected to Splunk",
            "info": {
                "host": service.host,
                "port": service.port,
                "username": service.username
            }
        }
    except SplunkConnectionError as e:
        logger.error(f"Splunk connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "details": {
                "host": os.getenv("SPLUNK_HOST", "localhost"),
                "port": os.getenv("SPLUNK_PORT", "8089")
            }
        }

# Then add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*", "MCP-Protocol-Version", "Mcp-Session-Id"],
    expose_headers=["MCP-Protocol-Version", "Mcp-Session-Id"]
)

# Mount MCP app with proper route handling
app.include_router(mcp.http_app().router, prefix="/mcp")
logger.info("MCP routes mounted at /mcp")

# MCP Standard HTTP Transport Endpoints
@app.post("/mcp")
async def handle_mcp_post(request: Request):
    """Handle MCP JSON-RPC messages via POST"""
    try:
        # Get the response from FastMCP
        mcp_response = await mcp.http_app()(request.scope, request.receive, request._send)
        
        # Ensure we have a response object
        if mcp_response is None:
            raise ValueError("MCP returned None response")
            
        # Set required headers
        mcp_response.headers["MCP-Protocol-Version"] = "2025-06-18"
        mcp_response.headers["Cache-Control"] = "no-cache"
        return mcp_response
        
    except Exception as e:
        logger.error(f"MCP POST handler error: {str(e)}")
        return Response(
            content=f"{{'error': '{str(e)}'}}",
            media_type="application/json",
            status_code=500,
            headers={
                "MCP-Protocol-Version": "2025-06-18",
                "Cache-Control": "no-cache"
            }
        )

@app.get("/mcp")
async def handle_mcp_get(request: Request):
    """Handle MCP SSE stream via GET"""
    try:
        # Get the response from FastMCP
        mcp_response = await mcp.http_app()(request.scope, request.receive, request._send)
        
        # Ensure we have a response object
        if mcp_response is None:
            raise ValueError("MCP returned None response")
            
        # Set required headers
        mcp_response.headers["MCP-Protocol-Version"] = "2025-06-18"
        mcp_response.headers["Cache-Control"] = "no-cache"
        return mcp_response
        
    except Exception as e:
        logger.error(f"MCP GET handler error: {str(e)}")
        return Response(
            content=f"{{'error': '{str(e)}'}}",
            media_type="text/event-stream",
            status_code=500,
            headers={
                "MCP-Protocol-Version": "2025-06-18",
                "Cache-Control": "no-cache"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8334,
        timeout_keep_alive=60,
        log_config=None  # Use our existing logging config
    )
