"""
Fixed Splunk MCP Server - Compatible with MCP Protocol
This version removes FastAPI dependencies from MCP tools and handles authentication properly
"""
print("SPLUNK MCP SERVER STARTING - FIXED VERSION")
from fastmcp import FastMCP
from fastapi import FastAPI, Response, Request, APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import logging
import os
from typing import Optional, Dict, Any, List
import time

# Import security modules
from .security import (
    security_middleware,
    security_logger,
    security_config,
    TokenManager,
    RoleBasedAccessControl,
    SecurityMiddleware
)
from .auth_middleware import (
    security_utils,
    security_headers,
    token_service,
    security_validator,
    get_current_user,
    require_permission,
    check_rate_limit
)
from .redis_manager import redis_manager

# Custom exceptions
class SplunkConnectionError(Exception):
    """Raised when connection to Splunk fails"""
    pass

class SplunkQueryError(Exception):
    """Raised when a Splunk query fails"""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails"""
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

# --- Request Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    roles: List[str]

class UserCreateRequest(BaseModel):
    username: str
    password: str
    roles: List[str]

class HealthResponse(BaseModel):
    status: str
    version: str
    services: List[str]
    authenticated: bool = False

# --- Monitoring Metrics ---
class SplunkMetrics:
    def __init__(self):
        self.connection_attempts = 0
        self.connection_successes = 0
        self.connection_failures = 0
        self.query_count = 0
        self.query_errors = 0
        self.query_timeouts = 0
        self.auth_attempts = 0
        self.auth_successes = 0
        self.auth_failures = 0

    def increment_connection_attempts(self): self.connection_attempts += 1
    def increment_connection_successes(self): self.connection_successes += 1
    def increment_connection_failures(self): self.connection_failures += 1
    def increment_query_count(self): self.query_count += 1
    def increment_query_errors(self): self.query_errors += 1
    def increment_query_timeouts(self): self.query_timeouts += 1
    def increment_auth_attempts(self): self.auth_attempts += 1
    def increment_auth_successes(self): self.auth_successes += 1
    def increment_auth_failures(self): self.auth_failures += 1

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
            },
            "authentication": {
                "attempts": self.auth_attempts,
                "successes": self.auth_successes,
                "failures": self.auth_failures,
                "success_rate": self.auth_successes / max(1, self.auth_attempts)
            }
        }

metrics = SplunkMetrics()

# --- User Management ---
class UserManager:
    """Simple in-memory user management for demo purposes"""
    
    def __init__(self):
        self.users = {
            "admin": {
                "password": self._hash_password("admin123"),
                "roles": ["admin"],
                "user_id": "admin"
            },
            "user": {
                "password": self._hash_password("user123"),
                "roles": ["user"],
                "user_id": "user"
            },
            "readonly": {
                "password": self._hash_password("readonly123"),
                "roles": ["readonly"],
                "user_id": "readonly"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        if username in self.users:
            hashed_password = self._hash_password(password)
            if self.users[username]["password"] == hashed_password:
                return {
                    "user_id": self.users[username]["user_id"],
                    "username": username,
                    "roles": self.users[username]["roles"]
                }
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        for username, user_data in self.users.items():
            if user_data["user_id"] == user_id:
                return {
                    "user_id": user_id,
                    "username": username,
                    "roles": user_data["roles"]
                }
        return None

user_manager = UserManager()

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

# Security scheme for API
security = HTTPBearer()

# Global variable to store the current user context (will be set by middleware)
current_user_context = None

def set_current_user(user_data: Dict[str, Any]):
    """Set the current user context for MCP tools"""
    global current_user_context
    current_user_context = user_data

def get_current_user_context() -> Optional[Dict[str, Any]]:
    """Get the current user context"""
    return current_user_context

def check_permission(permission: str) -> bool:
    """Check if current user has required permission"""
    user_data = get_current_user_context()
    if not user_data:
        return False
    return security_middleware.authorize_request(user_data, permission)

# MCP Tools - FIXED VERSION (without FastAPI dependencies)
@mcp.tool()
async def mcp_health_check() -> dict:
    """Health check for MCP server"""
    return {"status": "ok", "services": ["splunk", "redis"]}

@mcp.tool()
async def list_indexes() -> list:
    """List Splunk indexes (requires read:search permission)"""
    if not check_permission('read:search'):
        raise SplunkQueryError("Insufficient permissions: read:search required")
    
    try:
        indexes = get_splunk_service().indexes
        return [idx.name for idx in indexes] if indexes else []
    except Exception as e:
        logger.error(f"Error listing indexes: {e}")
        raise SplunkQueryError(f"Failed to list indexes: {str(e)}")

@mcp.tool()
async def splunk_search(
    query: str,
    earliest_time: str = "-24h",
    latest_time: str = "now",
    output_mode: str = "json",
    use_cache: bool = True
) -> dict:
    """Execute a Splunk search query and return results (requires read:search permission)"""
    if not check_permission('read:search'):
        raise SplunkQueryError("Insufficient permissions: read:search required")
    
    # Validate query for security
    is_valid, error_msg = security_validator.validate_splunk_query(query)
    if not is_valid:
        raise SplunkQueryError(f"Invalid query: {error_msg}")
    
    # Create cache key
    cache_key = f"{query}:{earliest_time}:{latest_time}:{output_mode}"
    
    # Check cache if enabled
    if use_cache:
        cached_result = redis_manager.get_cached_query(cache_key)
        if cached_result:
            logger.info("Returning cached search results")
            return cached_result
    
    from .search_helper import execute_splunk_search
    try:
        result = await execute_splunk_search(
            query,
            earliest_time=earliest_time,
            latest_time=latest_time,
            output_mode=output_mode
        )
        
        # Cache the result
        if use_cache:
            redis_manager.cache_query(cache_key, result, ttl=300)
        
        return result
    except SplunkQueryError as e:
        logger.error(f"Splunk search failed for query '{query}': {e}")
        raise

@mcp.tool()
async def get_itsi_services(service_name: Optional[str] = None) -> list:
    """Get ITSI services (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_services(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI services: {e}")
        raise SplunkQueryError(f"Failed to get ITSI services: {str(e)}")

@mcp.tool()
async def get_itsi_service_health(service_name: str) -> dict:
    """Get health status for a specific ITSI service (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_health(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI service health: {e}")
        raise SplunkQueryError(f"Failed to get ITSI service health: {str(e)}")

@mcp.tool()
async def get_itsi_kpis(service_name: Optional[str] = None) -> list:
    """Get ITSI KPIs (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_kpis(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI KPIs: {e}")
        raise SplunkQueryError(f"Failed to get ITSI KPIs: {str(e)}")

@mcp.tool()
async def get_itsi_alerts(service_name: Optional[str] = None) -> list:
    """Get ITSI alerts (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_alerts(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI alerts: {e}")
        raise SplunkQueryError(f"Failed to get ITSI alerts: {str(e)}")

@mcp.tool()
async def get_itsi_entities(service_name: Optional[str] = None) -> list:
    """Get ITSI service entities (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_entities(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI entities: {e}")
        raise SplunkQueryError(f"Failed to get ITSI entities: {str(e)}")

@mcp.tool()
async def get_itsi_entity_types() -> list:
    """Get ITSI entity types (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_entity_types()
    except Exception as e:
        logger.error(f"Error getting ITSI entity types: {e}")
        raise SplunkQueryError(f"Failed to get ITSI entity types: {str(e)}")

@mcp.tool()
async def get_itsi_glass_tables() -> list:
    """Get ITSI glass tables (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_glass_tables()
    except Exception as e:
        logger.error(f"Error getting ITSI glass tables: {e}")
        raise SplunkQueryError(f"Failed to get ITSI glass tables: {str(e)}")

@mcp.tool()
async def get_itsi_service_analytics(service_name: str, time_range: str = "-24h") -> dict:
    """Get analytics for an ITSI service (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_analytics(service_name, time_range)
    except Exception as e:
        logger.error(f"Error getting ITSI service analytics: {e}")
        raise SplunkQueryError(f"Failed to get ITSI service analytics: {str(e)}")

@mcp.tool()
async def get_itsi_deep_dives(service_name: Optional[str] = None) -> list:
    """Get ITSI deep dives (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_deep_dives(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI deep dives: {e}")
        raise SplunkQueryError(f"Failed to get ITSI deep dives: {str(e)}")

@mcp.tool()
async def get_itsi_home_views() -> list:
    """Get ITSI home views (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_home_views()
    except Exception as e:
        logger.error(f"Error getting ITSI home views: {e}")
        raise SplunkQueryError(f"Failed to get ITSI home views: {str(e)}")

@mcp.tool()
async def get_itsi_kpi_templates() -> list:
    """Get ITSI KPI templates (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_kpi_templates()
    except Exception as e:
        logger.error(f"Error getting ITSI KPI templates: {e}")
        raise SplunkQueryError(f"Failed to get ITSI KPI templates: {str(e)}")

@mcp.tool()
async def get_itsi_notable_events(service_name: Optional[str] = None, time_range: str = "-24h") -> list:
    """Get ITSI notable events (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_notable_events(service_name, time_range)
    except Exception as e:
        logger.error(f"Error getting ITSI notable events: {e}")
        raise SplunkQueryError(f"Failed to get ITSI notable events: {str(e)}")

@mcp.tool()
async def get_itsi_correlation_searches() -> list:
    """Get ITSI correlation searches (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_correlation_searches()
    except Exception as e:
        logger.error(f"Error getting ITSI correlation searches: {e}")
        raise SplunkQueryError(f"Failed to get ITSI correlation searches: {str(e)}")

@mcp.tool()
async def get_itsi_maintenance_calendars() -> list:
    """Get ITSI maintenance calendars (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_maintenance_calendars()
    except Exception as e:
        logger.error(f"Error getting ITSI maintenance calendars: {e}")
        raise SplunkQueryError(f"Failed to get ITSI maintenance calendars: {str(e)}")

@mcp.tool()
async def get_itsi_teams() -> list:
    """Get ITSI teams (requires read:itsi permission)"""
    if not check_permission('read:itsi'):
        raise SplunkQueryError("Insufficient permissions: read:itsi required")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_teams()
    except Exception as e:
        logger.error(f"Error getting ITSI teams: {e}")
        raise SplunkQueryError(f"Failed to get ITSI teams: {str(e)}")

# --- API Application ---
api_router = APIRouter()

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token"""
    metrics.increment_auth_attempts()
    
    user = user_manager.authenticate_user(request.username, request.password)
    if not user:
        metrics.increment_auth_failures()
        security_logger.log_authentication(
            user_id=request.username,
            success=False
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Check rate limit
    allowed, remaining = security_middleware.check_rate_limit(user['user_id'])
    if not allowed:
        security_logger.log_rate_limit(user_id=user['user_id'])
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    # Generate token
    token = security_middleware.token_manager.generate_token(
        user['user_id'],
        user['roles'],
        expires_in=security_config.token_expiry_hours
    )
    
    security_logger.log_authentication(
        user_id=user['user_id'],
        success=True
    )
    metrics.increment_auth_successes()
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=security_config.token_expiry_hours * 3600,
        user_id=user['user_id'],
        roles=user['roles']
    )

@api_router.post("/auth/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Refresh access token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Token required")
    
    token = credentials.credentials
    new_token = security_middleware.token_manager.refresh_token(token)
    
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"access_token": new_token, "token_type": "bearer"}

@api_router.get("/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Get current user information"""
    return {
        "user_id": current_user['user_id'],
        "username": current_user['username'],
        "roles": current_user['roles'],
        "permissions": security_middleware.rbac.get_user_permissions(current_user['roles'])
    }

@api_router.get("/metrics")
async def get_metrics_endpoint(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Get system metrics (requires admin role)"""
    if not security_middleware.authorize_request(current_user, 'read:*'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    redis_health = redis_manager.health_check()
    return {
        **metrics.get_metrics(),
        "redis": redis_health
    }

@api_router.get("/health")
async def health_check_endpoint():
    """Health check endpoint (public)"""
    redis_health = redis_manager.health_check()
    return {
        "status": "ok",
        "version": "1.0.0",
        "services": ["splunk", "redis"],
        "redis_details": redis_health
    }

@api_router.get("/redis/cache/stats")
async def get_cache_stats(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Get Redis cache statistics (requires admin role)"""
    if not security_middleware.authorize_request(current_user, 'read:*'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return redis_manager.get_cache_stats()

@api_router.post("/redis/cache/clear")
async def clear_cache(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Clear Redis cache (requires admin role)"""
    if not security_middleware.authorize_request(current_user, 'write:*'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    redis_manager.clear_cache()
    return {"message": "Cache cleared successfully"}

@api_router.get("/test-splunk-connection")
async def test_splunk_connection_endpoint(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Test Splunk connection (requires read:search permission)"""
    if not security_middleware.authorize_request(current_user, 'read:search'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        service = get_splunk_service()
        indexes = service.indexes
        return {
            "connected": True,
            "indexes_count": len([idx for idx in indexes]),
            "splunk_version": service.info["version"]
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }

# Create FastAPI app
root_app = FastAPI(title="Splunk MCP Server", version="1.0.0")

# Add CORS middleware
root_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
root_app.include_router(api_router, prefix="/api")

# --- MCP Router with Authentication ---
# Create dedicated MCP router with security
mcp_router = APIRouter()

@mcp_router.api_route("/{path:path}", methods=["GET", "POST"])
async def handle_mcp_requests(
    request: Request, 
    path: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Handle MCP requests with authentication"""
    # Authenticate request
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    user_data = security_middleware.authenticate_request(token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Set user context for MCP tools
    set_current_user(user_data)
    
    # Check rate limit
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = security_middleware.check_rate_limit(client_ip)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"X-RateLimit-Remaining": str(remaining)}
        )
    
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
        "state": {"user": user_data}
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
    
    # Clear user context after request
    set_current_user(None)
    
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
        log_config=None,
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE")
    )