print("SPLUNK MCP SERVER STARTING")  # Module-level print to verify execution
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

async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Get current authenticated user from token"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials required"
        )
    
    token = credentials.credentials
    user_data = security_middleware.authenticate_request(token)
    
    if not user_data:
        security_logger.log_authentication(
            user_id="unknown",
            success=False
        )
        metrics.increment_auth_failures()
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    # Get full user data
    user = user_manager.get_user_by_id(user_data.get('user_id'))
    if not user:
        metrics.increment_auth_failures()
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    security_logger.log_authentication(
        user_id=user['user_id'],
        success=True
    )
    metrics.increment_auth_successes()
    
    return user

def require_permission(permission: str):
    """Dependency for requiring specific permissions"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
        if not security_middleware.authorize_request(current_user, permission):
            security_logger.log_authorization(
                user_id=current_user.get('user_id', 'unknown'),
                permission=permission,
                success=False
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: {permission}"
            )
        
        security_logger.log_authorization(
            user_id=current_user.get('user_id', 'unknown'),
            permission=permission,
            success=True
        )
        
        return current_user
    
    return permission_checker

# MCP Tools with Security
@mcp.tool()
async def mcp_health_check() -> dict:
    return {"status": "ok", "services": ["splunk", "redis"]}

@mcp.tool()
async def list_indexes(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> list:
    """List Splunk indexes (requires read:search permission)"""
    if not security_middleware.authorize_request(current_user, 'read:search'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
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
    output_mode: str = "json",
    use_cache: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> dict:
    """Execute a Splunk search query and return results (requires read:search permission)"""
    if not security_middleware.authorize_request(current_user, 'read:search'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Validate query for security
    is_valid, error_msg = security_validator.validate_splunk_query(query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid query: {error_msg}")
    
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
async def get_itsi_services(
    service_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI services (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_services(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI services: {e}")
        raise SplunkQueryError("Failed to get ITSI services")

@mcp.tool()
async def get_itsi_service_health(
    service_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> dict:
    """Get health status for a specific ITSI service (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_health(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI service health: {e}")
        raise SplunkQueryError("Failed to get ITSI service health")

@mcp.tool()
async def get_itsi_kpis(
    service_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI KPIs (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_kpis(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI KPIs: {e}")
        raise SplunkQueryError("Failed to get ITSI KPIs")

@mcp.tool()
async def get_itsi_alerts(
    service_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI alerts (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_alerts(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI alerts: {e}")
        raise SplunkQueryError("Failed to get ITSI alerts")

@mcp.tool()
async def get_itsi_entities(
    service_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI service entities (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_entities(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI entities: {e}")
        raise SplunkQueryError("Failed to get ITSI entities")

@mcp.tool()
async def get_itsi_entity_types(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI entity types (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_entity_types()
    except Exception as e:
        logger.error(f"Error getting ITSI entity types: {e}")
        raise SplunkQueryError("Failed to get ITSI entity types")

@mcp.tool()
async def get_itsi_glass_tables(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI glass tables (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_glass_tables()
    except Exception as e:
        logger.error(f"Error getting ITSI glass tables: {e}")
        raise SplunkQueryError("Failed to get ITSI glass tables")

@mcp.tool()
async def get_itsi_service_analytics(
    service_name: str,
    time_range: str = "-24h",
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> dict:
    """Get analytics for an ITSI service (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_service_analytics(service_name, time_range)
    except Exception as e:
        logger.error(f"Error getting ITSI service analytics: {e}")
        raise SplunkQueryError("Failed to get ITSI service analytics")

@mcp.tool()
async def get_itsi_deep_dives(
    service_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI deep dives (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_deep_dives(service_name)
    except Exception as e:
        logger.error(f"Error getting ITSI deep dives: {e}")
        raise SplunkQueryError("Failed to get ITSI deep dives")

@mcp.tool()
async def get_itsi_home_views(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI home views (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_home_views()
    except Exception as e:
        logger.error(f"Error getting ITSI home views: {e}")
        raise SplunkQueryError("Failed to get ITSI home views")

@mcp.tool()
async def get_itsi_kpi_templates(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI KPI templates (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_kpi_templates()
    except Exception as e:
        logger.error(f"Error getting ITSI KPI templates: {e}")
        raise SplunkQueryError("Failed to get ITSI KPI templates")

@mcp.tool()
async def get_itsi_notable_events(
    service_name: Optional[str] = None,
    time_range: str = "-24h",
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI notable events (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_notable_events(service_name, time_range)
    except Exception as e:
        logger.error(f"Error getting ITSI notable events: {e}")
        raise SplunkQueryError("Failed to get ITSI notable events")

@mcp.tool()
async def get_itsi_correlation_searches(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI correlation searches (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_correlation_searches()
    except Exception as e:
        logger.error(f"Error getting ITSI correlation searches: {e}")
        raise SplunkQueryError("Failed to get ITSI correlation searches")

@mcp.tool()
async def get_itsi_maintenance_calendars(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI maintenance calendars (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_maintenance_calendars()
    except Exception as e:
        logger.error(f"Error getting ITSI maintenance calendars: {e}")
        raise SplunkQueryError("Failed to get ITSI maintenance calendars")

@mcp.tool()
async def get_itsi_teams(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> list:
    """Get ITSI teams (requires read:itsi permission)"""
    if not security_middleware.authorize_request(current_user, 'read:itsi'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from .itsi_helper import ITSIHelper
    try:
        service = get_splunk_service()
        itsi_helper = ITSIHelper(service)
        return itsi_helper.get_teams()
    except Exception as e:
        logger.error(f"Error getting ITSI teams: {e}")
        raise SplunkQueryError("Failed to get ITSI teams")

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
    """Get Redis cache statistics"""
    if not security_middleware.authorize_request(current_user, 'read:*'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not redis_manager.is_connected():
        raise HTTPException(status_code=503, detail="Redis not available")
    
    return redis_manager.health_check()

@api_router.post("/redis/cache/clear")
async def clear_cache(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Clear Redis cache"""
    if not security_middleware.authorize_request(current_user, 'write:*'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not redis_manager.is_connected():
        raise HTTPException(status_code=503, detail="Redis not available")
    
    # This would require implementing cache clearing functionality
    return {"message": "Cache clearing functionality to be implemented"}

@api_router.get("/test-splunk-connection")
async def test_splunk_connection_endpoint(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Test Splunk connection (requires read:search permission)"""
    if not security_middleware.authorize_request(current_user, 'read:search'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        service = get_splunk_service()
        return {"status": "success", "message": "Successfully connected to Splunk",
                "info": {"host": service.host, "port": service.port, "username": service.username}}
    except SplunkConnectionError as e:
        logger.error(f"Splunk connection test failed: {e}")
        return {"status": "error", "message": str(e),
                "details": {"host": os.getenv("SPLUNK_HOST"), "port": os.getenv("SPLUNK_PORT")}}

# --- Root Application Assembly ---
root_app = FastAPI(
    title="Splunk MCP Server",
    description="Secure Splunk MCP server with authentication and authorization",
    version="1.0.0"
)

# --- Lifespan Management ---
@root_app.on_event("startup")
async def startup_event():
    logger.info("Application lifespan startup")
    logger.info("Security configuration validated" if security_config.validate_config() else "Security configuration invalid")

@root_app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application lifespan shutdown")

# --- Security Middleware ---
@root_app.middleware("http")
async def security_middleware_func(request: Request, call_next):
    """Security middleware for all requests"""
    start_time = time.time()
    
    # Add security headers
    response = await call_next(request)
    response = security_headers.add_security_headers(response)
    
    # Add rate limit headers
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = security_middleware.check_rate_limit(client_ip)
    
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    # Log request
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Apply middleware to the root app
root_app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*", "Authorization", "MCP-Protocol-Version", "Mcp-Session-Id"],
    expose_headers=["MCP-Protocol-Version", "Mcp-Session-Id", "X-RateLimit-Remaining"]
)

# Mount the sub-applications
api_app = FastAPI(routes=api_router.routes)
root_app.mount("/api", api_app)

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
