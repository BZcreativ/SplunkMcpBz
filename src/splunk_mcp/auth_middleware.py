"""
Authentication middleware for FastMCP integration
Provides security middleware for MCP server endpoints
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .security import (
    security_middleware, 
    security_logger, 
    security_config,
    TokenManager,
    RoleBasedAccessControl
)

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
token_manager = TokenManager(security_config.secret_key)
rbac = RoleBasedAccessControl()

class AuthMiddleware:
    """Authentication middleware for MCP server"""
    
    def __init__(self):
        self.allowed_origins = security_config.allowed_origins
        self.ssl_verify = security_config.ssl_verify
        
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def add_cors_middleware(self, app):
        """Add CORS middleware with security settings"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Reset"]
        )
        
    def add_security_middleware(self, app):
        """Add security middleware"""
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on your needs
        )

async def get_current_user(
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
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    security_logger.log_authentication(
        user_id=user_data.get('user_id', 'unknown'),
        success=True
    )
    
    return user_data

def require_permission(permission: str):
    """Dependency for requiring specific permissions"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
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

def check_rate_limit(user_id: str) -> bool:
    """Check rate limit for user"""
    allowed, remaining = security_middleware.check_rate_limit(user_id)
    
    if not allowed:
        security_logger.log_rate_limit(user_id=user_id)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"X-RateLimit-Remaining": str(remaining)}
        )
    
    return True

class SecurityHeaders:
    """Security headers for responses"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        for key, value in headers.items():
            response.headers[key] = value
        
        return response

class TokenService:
    """Token management service"""
    
    @staticmethod
    def generate_api_key(user_id: str, roles: list) -> str:
        """Generate API key for user"""
        return token_manager.generate_token(user_id, roles, expires_in=8760)  # 1 year
    
    @staticmethod
    def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key"""
        return security_middleware.authenticate_request(api_key)
    
    @staticmethod
    def revoke_token(token: str) -> bool:
        """Revoke token (implement token blacklist)"""
        # TODO: Implement token blacklist
        return True

class SecurityValidator:
    """Input validation service"""
    
    @staticmethod
    def validate_splunk_query(query: str) -> tuple[bool, str]:
        """Validate Splunk query for security"""
        dangerous_patterns = [
            'delete', 'drop', 'alter', 'create', 'insert',
            'update', 'exec', 'system', 'shell', 'cmd'
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if pattern in query_lower:
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, ""
    
    @staticmethod
    def validate_input_data(data: Dict[str, Any]) -> tuple[bool, list]:
        """Validate input data"""
        return security_middleware.validate_input(data)

# Security utilities
security_utils = AuthMiddleware()
security_headers = SecurityHeaders()
token_service = TokenService()
security_validator = SecurityValidator()

# Export for use in main.py
__all__ = [
    'security_utils',
    'security_headers',
    'token_service',
    'security_validator',
    'get_current_user',
    'require_permission',
    'check_rate_limit'
]
