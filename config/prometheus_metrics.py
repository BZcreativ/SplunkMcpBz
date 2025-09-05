"""
Prometheus Metrics Integration for Splunk MCP Server
Provides comprehensive metrics collection and exposure for monitoring
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from datetime import datetime
import functools

# Configure logging
logger = logging.getLogger(__name__)

# Create a custom registry for our metrics
REGISTRY = CollectorRegistry()

# Application Info
APP_INFO = Info(
    'mcp_splunk_app_info',
    'Application information',
    registry=REGISTRY,
    labelnames=['version', 'environment', 'deployment']
)

# Request Metrics
REQUEST_COUNT = Counter(
    'mcp_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code', 'user_role'],
    registry=REGISTRY
)

REQUEST_DURATION = Histogram(
    'mcp_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
    registry=REGISTRY
)

# Authentication Metrics
AUTH_ATTEMPTS = Counter(
    'mcp_auth_attempts_total',
    'Total authentication attempts',
    ['username', 'status', 'failure_reason'],
    registry=REGISTRY
)

AUTH_DURATION = Histogram(
    'mcp_auth_duration_seconds',
    'Authentication duration',
    ['auth_type'],
    registry=REGISTRY
)

ACTIVE_SESSIONS = Gauge(
    'mcp_active_sessions',
    'Number of active user sessions',
    ['user_role'],
    registry=REGISTRY
)

# Splunk Connection Metrics
SPLUNK_CONNECTIONS = Gauge(
    'mcp_splunk_connections_active',
    'Number of active Splunk connections',
    registry=REGISTRY
)

SPLUNK_CONNECTION_ERRORS = Counter(
    'mcp_splunk_connection_errors_total',
    'Total Splunk connection errors',
    ['error_type'],
    registry=REGISTRY
)

SPLUNK_QUERY_DURATION = Histogram(
    'mcp_splunk_query_duration_seconds',
    'Splunk query execution time',
    ['query_type', 'index'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
    registry=REGISTRY
)

SPLUNK_QUERY_ERRORS = Counter(
    'mcp_splunk_query_errors_total',
    'Total Splunk query errors',
    ['error_type', 'query_type'],
    registry=REGISTRY
)

# Redis Metrics
REDIS_CONNECTIONS = Gauge(
    'mcp_redis_connections_active',
    'Number of active Redis connections',
    registry=REGISTRY
)

REDIS_OPERATIONS = Counter(
    'mcp_redis_operations_total',
    'Total Redis operations',
    ['operation', 'status'],
    registry=REGISTRY
)

REDIS_OPERATION_DURATION = Histogram(
    'mcp_redis_operation_duration_seconds',
    'Redis operation duration',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
    registry=REGISTRY
)

CACHE_HITS = Counter(
    'mcp_cache_hits_total',
    'Total cache hits',
    ['cache_type'],
    registry=REGISTRY
)

CACHE_MISSES = Counter(
    'mcp_cache_misses_total',
    'Total cache misses',
    ['cache_type'],
    registry=REGISTRY
)

# ITSI Metrics
ITSI_OPERATIONS = Counter(
    'mcp_itsi_operations_total',
    'Total ITSI operations',
    ['operation', 'object_type', 'status'],
    registry=REGISTRY
)

ITSI_OPERATION_DURATION = Histogram(
    'mcp_itsi_operation_duration_seconds',
    'ITSI operation duration',
    ['operation', 'object_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=REGISTRY
)

# Rate Limiting Metrics
RATE_LIMIT_HITS = Counter(
    'mcp_rate_limit_hits_total',
    'Total rate limit violations',
    ['user_id', 'endpoint'],
    registry=REGISTRY
)

# System Metrics
MEMORY_USAGE = Gauge(
    'mcp_memory_usage_bytes',
    'Memory usage in bytes',
    ['type'],
    registry=REGISTRY
)

CPU_USAGE = Gauge(
    'mcp_cpu_usage_percent',
    'CPU usage percentage',
    registry=REGISTRY
)

# Business Logic Metrics
ACTIVE_SERVICES = Gauge(
    'mcp_itsi_services_active',
    'Number of active ITSI services',
    registry=REGISTRY
)

ACTIVE_KPIS = Gauge(
    'mcp_itsi_kpis_active',
    'Number of active ITSI KPIs',
    registry=REGISTRY
)

ACTIVE_ALERTS = Gauge(
    'mcp_itsi_alerts_active',
    'Number of active ITSI alerts',
    ['severity'],
    registry=REGISTRY
)

class MetricsCollector:
    """Centralized metrics collection and management"""
    
    def __init__(self, app_version: str = "1.0.0", environment: str = "production"):
        self.app_version = app_version
        self.environment = environment
        self.start_time = datetime.now()
        
        # Set application info
        APP_INFO.info({
            'version': app_version,
            'environment': environment,
            'deployment': 'docker'
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, 
                      duration: float, user_role: str = "anonymous"):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            user_role=user_role
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_auth_attempt(self, username: str, status: str, 
                           failure_reason: str = "", duration: float = 0.0):
        """Record authentication attempt"""
        AUTH_ATTEMPTS.labels(
            username=username,
            status=status,
            failure_reason=failure_reason or "none"
        ).inc()
        
        if duration > 0:
            AUTH_DURATION.labels(auth_type="login").observe(duration)
    
    def record_splunk_query(self, query_type: str, index: str, 
                           duration: float, success: bool = True,
                           error_type: str = ""):
        """Record Splunk query metrics"""
        if success:
            SPLUNK_QUERY_DURATION.labels(
                query_type=query_type,
                index=index
            ).observe(duration)
        else:
            error_type_label = error_type or "unknown"
            SPLUNK_QUERY_ERRORS.labels(
                error_type=error_type_label,
                query_type=query_type
            ).inc()
    
    def record_redis_operation(self, operation: str, duration: float, 
                              success: bool = True):
        """Record Redis operation metrics"""
        REDIS_OPERATIONS.labels(
            operation=operation,
            status="success" if success else "failure"
        ).inc()
        
        REDIS_OPERATION_DURATION.labels(
            operation=operation
        ).observe(duration)
    
    def record_cache_operation(self, cache_type: str, hit: bool = True):
        """Record cache operation"""
        if hit:
            CACHE_HITS.labels(cache_type=cache_type).inc()
        else:
            CACHE_MISSES.labels(cache_type=cache_type).inc()
    
    def record_itsi_operation(self, operation: str, object_type: str,
                             duration: float, success: bool = True):
        """Record ITSI operation metrics"""
        ITSI_OPERATIONS.labels(
            operation=operation,
            object_type=object_type,
            status="success" if success else "failure"
        ).inc()
        
        ITSI_OPERATION_DURATION.labels(
            operation=operation,
            object_type=object_type
        ).observe(duration)
    
    def record_rate_limit_hit(self, user_id: str, endpoint: str):
        """Record rate limit violation"""
        RATE_LIMIT_HITS.labels(
            user_id=user_id,
            endpoint=endpoint
        ).inc()
    
    def update_gauge_metrics(self, metric_name: str, value: float, 
                           labels: Optional[Dict[str, str]] = None):
        """Update gauge metrics"""
        if metric_name == "active_sessions":
            if labels and "user_role" in labels:
                ACTIVE_SESSIONS.labels(user_role=labels["user_role"]).set(value)
        elif metric_name == "splunk_connections":
            SPLUNK_CONNECTIONS.set(value)
        elif metric_name == "redis_connections":
            REDIS_CONNECTIONS.set(value)
        elif metric_name == "memory_usage":
            if labels and "type" in labels:
                MEMORY_USAGE.labels(type=labels["type"]).set(value)
        elif metric_name == "cpu_usage":
            CPU_USAGE.set(value)
        elif metric_name == "active_services":
            ACTIVE_SERVICES.set(value)
        elif metric_name == "active_kpis":
            ACTIVE_KPIS.set(value)
        elif metric_name == "active_alerts" and labels:
            if "severity" in labels:
                ACTIVE_ALERTS.labels(severity=labels["severity"]).set(value)

def metrics_middleware(func: Callable) -> Callable:
    """Decorator to automatically collect metrics for functions"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = kwargs.get('method', 'unknown')
        endpoint = kwargs.get('endpoint', 'unknown')
        user_role = kwargs.get('user_role', 'anonymous')
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                user_role=user_role
            ).inc()
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    return wrapper

# Global metrics collector instance
metrics_collector = MetricsCollector()

def get_metrics() -> str:
    """Get Prometheus metrics in text format"""
    return generate_latest(REGISTRY).decode('utf-8')

def get_metrics_content_type() -> str:
    """Get the content type for Prometheus metrics"""
    return CONTENT_TYPE_LATEST

# Example usage and testing
if __name__ == "__main__":
    # Test metrics collection
    print("Testing Prometheus metrics integration...")
    
    # Record some sample metrics
    metrics_collector.record_request("GET", "/health", 200, 0.1, "admin")
    metrics_collector.record_auth_attempt("admin", "success", duration=0.05)
    metrics_collector.record_splunk_query("search", "_internal", 1.5, success=True)
    metrics_collector.record_cache_operation("query", hit=True)
    metrics_collector.record_itsi_operation("list", "services", 0.3, success=True)
    
    # Update gauge metrics
    metrics_collector.update_gauge_metrics("active_sessions", 5, {"user_role": "admin"})
    metrics_collector.update_gauge_metrics("splunk_connections", 3)
    metrics_collector.update_gauge_metrics("active_services", 25)
    
    # Get metrics
    metrics_output = get_metrics()
    print("Generated metrics:")
    print(metrics_output[:500] + "..." if len(metrics_output) > 500 else metrics_output)