"""
Security module for Splunk MCP server
Provides authentication, authorization, and security utilities
"""

import os
import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration management"""
    
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', Fernet.generate_key())
        self.token_expiry_hours = int(os.getenv('TOKEN_EXPIRY_HOURS', '24'))
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '100'))
        self.ssl_verify = os.getenv('VERIFY_SSL', 'false').lower() == 'true'
        self.allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        
    def validate_config(self) -> bool:
        """Validate security configuration"""
        if not self.secret_key:
            logger.error("SECRET_KEY not configured")
            return False
        return True

class TokenManager:
    """JWT token management for authentication"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = 'HS256'
        
    def generate_token(self, user_id: str, roles: List[str], expires_in: int = 24) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'roles': roles,
            'exp': datetime.utcnow() + timedelta(hours=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token"""
        payload = self.verify_token(token)
        if payload:
            # Remove old expiration and create new token
            payload.pop('exp', None)
            payload.pop('iat', None)
            return self.generate_token(
                payload['user_id'], 
                payload['roles'], 
                expires_in=24
            )
        return None

class RoleBasedAccessControl:
    """Role-based access control system"""
    
    def __init__(self):
        self.roles = {
            'admin': {
                'permissions': [
                    'read:*', 'write:*', 'delete:*', 'create:*',
                    'itsi:*', 'search:*', 'config:*'
                ]
            },
            'user': {
                'permissions': [
                    'read:itsi', 'read:search', 'write:itsi',
                    'create:itsi', 'delete:itsi'
                ]
            },
            'readonly': {
                'permissions': [
                    'read:itsi', 'read:search'
                ]
            }
        }
        
    def has_permission(self, user_roles: List[str], permission: str) -> bool:
        """Check if user has required permission"""
        for role in user_roles:
            if role in self.roles:
                role_perms = self.roles[role]['permissions']
                # Check exact match and wildcard permissions
                if permission in role_perms or any(
                    perm.endswith('*') and permission.startswith(perm[:-1])
                    for perm in role_perms
                ):
                    return True
        return False
    
    def get_user_permissions(self, user_roles: List[str]) -> List[str]:
        """Get all permissions for user roles"""
        permissions = []
        for role in user_roles:
            if role in self.roles:
                permissions.extend(self.roles[role]['permissions'])
        return list(set(permissions))

class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = {}  # user_id -> list of timestamps
        
    def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed for user"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        if user_id not in self.requests:
            self.requests[user_id] = []
            
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
            
        return False
    
    def get_remaining_requests(self, user_id: str) -> int:
        """Get remaining requests for user"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        if user_id not in self.requests:
            return self.max_requests
            
        recent_requests = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(recent_requests))

class SecurityMiddleware:
    """Security middleware for request handling"""
    
    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        self.token_manager = TokenManager(security_config.secret_key)
        self.rbac = RoleBasedAccessControl()
        self.rate_limiter = RateLimiter(
            max_requests=security_config.max_requests_per_minute
        )
        
    def authenticate_request(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate request with token"""
        if not token:
            return None
            
        # Remove Bearer prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
            
        return self.token_manager.verify_token(token)
    
    def authorize_request(self, user_data: Dict[str, Any], permission: str) -> bool:
        """Authorize request based on user roles"""
        if not user_data or 'roles' not in user_data:
            return False
            
        return self.rbac.has_permission(user_data['roles'], permission)
    
    def check_rate_limit(self, user_id: str) -> tuple[bool, int]:
        """Check rate limit for user"""
        allowed = self.rate_limiter.is_allowed(user_id)
        remaining = self.rate_limiter.get_remaining_requests(user_id)
        return allowed, remaining
    
    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate input data"""
        errors = []
        
        # Check for SQL injection patterns
        sql_patterns = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION']
        for key, value in data.items():
            if isinstance(value, str):
                upper_value = value.upper()
                if any(pattern in upper_value for pattern in sql_patterns):
                    errors.append(f"Potential SQL injection in field '{key}'")
        
        # Check for XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        for key, value in data.items():
            if isinstance(value, str):
                lower_value = value.lower()
                if any(pattern in lower_value for pattern in xss_patterns):
                    errors.append(f"Potential XSS in field '{key}'")
        
        return len(errors) == 0, errors

class SecurityLogger:
    """Security event logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        
    def log_authentication(self, user_id: str, success: bool, ip: str = None):
        """Log authentication attempt"""
        self.logger.info(json.dumps({
            'event': 'authentication',
            'user_id': user_id,
            'success': success,
            'ip': ip,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
    def log_authorization(self, user_id: str, permission: str, success: bool, ip: str = None):
        """Log authorization attempt"""
        self.logger.info(json.dumps({
            'event': 'authorization',
            'user_id': user_id,
            'permission': permission,
            'success': success,
            'ip': ip,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
    def log_rate_limit(self, user_id: str, ip: str = None):
        """Log rate limit violation"""
        self.logger.warning(json.dumps({
            'event': 'rate_limit_exceeded',
            'user_id': user_id,
            'ip': ip,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log generic security event"""
        self.logger.warning(json.dumps({
            'event': event_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }))

# Security decorators
def require_auth(permission: str = None):
    """Decorator for requiring authentication and authorization"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This will be integrated with FastMCP
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(max_requests: int = 100):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This will be integrated with FastMCP
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Initialize security components
security_config = SecurityConfig()
security_middleware = SecurityMiddleware(security_config)
security_logger = SecurityLogger()
