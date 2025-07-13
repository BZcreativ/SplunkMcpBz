print("SPLUNK MCP SERVER STARTING")  # Module-level print to verify execution
from fastmcp import FastMCP
from fastapi import FastAPI, Response, Request, APIRouter
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Custom exceptions
class SplunkConnectionError(Exception):
    """Raised when connection to Splunk fails"""
    pass

class SplunkQueryError(Exception):
    """Raised when a Splunk query fails"""
    pass

# Initialize logging first
print("Initializing logging configuration")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('mcp.protocol')
logger.info("Logger successfully initialized")

# --- Monitoring Metrics ---
class SplunkMetrics:
    def __init__(self):
        self.connection_attempts = 0
        self.connection_successes = 0
        self.connection_failures = 0
        self.query_count = 0
        self.query_errors = 0
        self.query_timeouts = 0

    def increment_connection_attempts(self): self.connection_attempts += 1
    def increment_connection_successes(self): self.connection_successes += 1
    def increment_connection_failures(self): self.connection_failures += 1
    def increment_query_count(self): self.query_count += 1
    def increment_query_errors(self): self.query_errors += 1
    def increment_query_timeouts(self): self.query_timeouts += 1

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

# --- Splunk Service ---
def get_splunk_service(max_retries: int = 3):
    import splunklib.client as client
    import time
    last_error = None
    for attempt in range(max_retries):
        metrics.increment_connection_attempts()
        try:
            host, port, scheme, token = (os.getenv("SPLUNK_HOST", "localhost"), int(os.getenv("SPLUNK_PORT", "8089")),
                                         os.getenv("SPLUNK_SCHEME", "https"), os.getenv("SPLUNK_TOKEN"))
            logger.debug(f"Attempting Splunk connection to {scheme}://{host}:{port}")
            logger.debug("Using token: *****")
            service = client.connect(host=host, port=port, splunkToken=token, scheme=scheme)
            metrics.increment_connection_successes()
            return service
        except Exception as e:
            last_error = e
            metrics.increment_connection_failures()
            logger.warning(f"Splunk connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise SplunkConnectionError(f"Failed to connect to Splunk after {max_retries} attempts: {last_error}")

# --- MCP Application ---
mcp = FastMCP("SplunkMCP")
logger.info("MCP initialized")

@mcp.tool()
async def mcp_health_check() -> dict:
    return {"status": "ok", "services": ["splunk", "redis"]}

@mcp.tool()
async def list_indexes() -> list:
    try:
        indexes = get_splunk_service().indexes
        return [idx.name for idx in indexes] if indexes else []
    except Exception as e:
        logger.error(f"Error listing indexes: {e}")
        raise SplunkQueryError("Failed to list indexes")

@mcp.tool()
async def splunk_search(
    query: str,
    earliest_time: str = "-24h",
    latest_time: str = "now",
    output_mode: str = "json"
) -> dict:
    """Execute a Splunk search query and return results"""
    from .search_helper import execute_splunk_search
    try:
        return await execute_splunk_search(
            query,
            earliest_time=earliest_time,
            latest_time=latest_time,
            output_mode=output_mode
        )
    except SplunkQueryError as e:
        logger.error(f"Splunk search failed for query '{query}': {e}")
        raise

@mcp.tool()
async def get_itsi_services(service_name: Optional[str] = None) -> list:
    """Get ITSI services"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_services(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI services: {e}")
        raise SplunkQueryError("Failed to get ITSI services")

@mcp.tool()
async def get_itsi_service_health(service_name: str) -> dict:
    """Get health status for a specific ITSI service"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_health(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI service health: {e}")
        raise SplunkQueryError("Failed to get ITSI service health")

@mcp.tool()
async def get_itsi_kpis(service_name: Optional[str] = None) -> list:
    """Get ITSI KPIs"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_kpis(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI KPIs: {e}")
        raise SplunkQueryError("Failed to get ITSI KPIs")

@mcp.tool()
async def get_itsi_alerts(service_name: Optional[str] = None) -> list:
    """Get ITSI alerts"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_alerts(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI alerts: {e}")
        raise SplunkQueryError("Failed to get ITSI alerts")

@mcp.tool()
async def get_itsi_entities(service_name: Optional[str] = None) -> list:
    """Get ITSI service entities"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_entities(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI entities: {e}")
        raise SplunkQueryError("Failed to get ITSI entities")

@mcp.tool()
async def get_itsi_entity_types() -> list:
    """Get ITSI entity types"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_entity_types()
    except Exception as e:
        logger.error(f"Error getting ITSI entity types: {e}")
        raise SplunkQueryError("Failed to get ITSI entity types")

@mcp.tool()
async def get_itsi_glass_tables() -> list:
    """Get ITSI glass tables"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_glass_tables()
    except Exception as e:
        logger.error(f"Error getting ITSI glass tables: {e}")
        raise SplunkQueryError("Failed to get ITSI glass tables")

@mcp.tool()
async def get_itsi_service_analytics(service_name: str, time_range: str = "-24h") -> dict:
    """Get analytics for an ITSI service"""
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_analytics(service_name, time_range)
    except Exception as e:
        logger.error(f"Error getting ITSI service analytics: {e}")
        raise SplunkQueryError("Failed to get ITSI service analytics")

# --- API Application ---
api_router = APIRouter()

@api_router.get("/metrics")
async def get_metrics_endpoint():
    return metrics.get_metrics()

@api_router.get("/health")
async def health_check_endpoint():
    return {"status": "ok", "version": "1.0.0", "services": ["splunk", "redis"]}

@api_router.get("/test-splunk-connection")
async def test_splunk_connection_endpoint():
    try:
        service = get_splunk_service()
        return {"status": "success", "message": "Successfully connected to Splunk",
                "info": {"host": service.host, "port": service.port, "username": service.username}}
    except SplunkConnectionError as e:
        logger.error(f"Splunk connection test failed: {e}")
        return {"status": "error", "message": str(e),
                "details": {"host": os.getenv("SPLUNK_HOST"), "port": os.getenv("SPLUNK_PORT")}}

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application lifespan startup")
    # FastMCP's lifespan manages its own resources
    async with mcp.http_app().router.lifespan_context(mcp.http_app()):
        yield
    logger.info("Application lifespan shutdown")

# --- Root Application Assembly ---
root_app = FastAPI(lifespan=lifespan)

# Apply middleware to the root app
root_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*", "MCP-Protocol-Version", "Mcp-Session-Id"],
    expose_headers=["MCP-Protocol-Version", "Mcp-Session-Id"]
)

@root_app.middleware("http")
async def add_protocol_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["MCP-Protocol-Version"] = "2025-07-13"
    response.headers["Cache-Control"] = "no-cache"
    return response

# Mount the sub-applications
api_app = FastAPI(routes=api_router.routes)
root_app.mount("/api", api_app)

# Create dedicated MCP router
mcp_router = APIRouter()

@mcp_router.api_route("/{path:path}", methods=["GET", "POST"])
async def handle_mcp_requests(request: Request, path: str):
    # Create proper ASGI scope for MCP
    scope = {
        "type": "http",
        "method": request.method,
        "path": f"/{path}" if path else "/",
        "raw_path": f"/{path}".encode() if path else b"/",
        "query_string": request.url.query.encode(),
        "headers": [(k.lower().encode(), v.encode()) for k, v in request.headers.items()],
        "client": request.client,
        "server": request.url.hostname,
        "scheme": request.url.scheme,
        "root_path": "",
        "app": root_app,
        "state": {}
    }
    
    # Forward request to MCP app with proper ASGI call
    async def receive():
        if request.method == "POST":
            body = await request.body()
            return {
                "type": "http.request",
                "body": body,
                "more_body": False
            }
        return {"type": "http.request"}
    
    # Handle ASGI response
    response_headers = []
    response_body = b""
    
    async def send(message):
        nonlocal response_headers, response_body
        if message["type"] == "http.response.start":
            response_headers = message["headers"]
        elif message["type"] == "http.response.body":
            response_body += message.get("body", b"")
    
    await mcp.http_app()(scope, receive, send)
    
    return Response(
        content=response_body,
        status_code=200,
        headers=dict(
            (k.decode(), v.decode()) 
            for k, v in response_headers
            if k != b"content-length"
        )
    )

# Mount MCP router with proper path handling
root_app.include_router(mcp_router, prefix="/mcp")

# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        root_app,
        host="0.0.0.0",
        port=8334,
        timeout_keep_alive=60,
        log_config=None
    )
