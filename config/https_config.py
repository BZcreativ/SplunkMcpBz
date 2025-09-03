
"""
HTTPS/SSL Configuration for Splunk MCP Server
Provides SSL/TLS configuration for production deployments
"""

import ssl
import os
from typing import Optional, Dict, Any
from pathlib import Path

class HTTPSConfig:
    """SSL/TLS configuration management"""
    
    def __init__(self):
        self.ssl_keyfile = os.getenv("SSL_KEYFILE")
        self.ssl_certfile = os.getenv("SSL_CERTFILE")
        self.ssl_ca_certs = os.getenv("SSL_CA_CERTS")
        self.ssl_ciphers = os.getenv(
            "SSL_CIPHERS",
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
        )
        self.ssl_protocol = os.getenv("SSL_PROTOCOL", "TLSv1.2")
        
    def is_ssl_enabled(self) -> bool:
        """Check if SSL is properly configured"""
        return bool(self.ssl_keyfile and self.ssl_certfile)
    
    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for HTTPS"""
        if not self.is_ssl_enabled():
            return None
            
        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(
                certfile=self.ssl_certfile,
                keyfile=self.ssl_keyfile
            )
            
            if self.ssl_ca_certs:
                context.load_verify_locations(self.ssl_ca_certs)
                
            # Security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers(self.ssl_ciphers)
            
            # Disable insecure protocols
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            
            return context
            
        except Exception as e:
            raise RuntimeError(f"Failed to create SSL context: {e}")
    
    def get_uvicorn_ssl_config(self) -> Dict[str, Any]:
        """Get SSL configuration for Uvicorn"""
        if not self.is_ssl_enabled():
            return {}
            
        return {
            "ssl_keyfile": self.ssl_keyfile,
            "ssl_certfile": self.ssl_certfile,
            "ssl_ca_certs": self.ssl_ca_certs,
            "ssl_ciphers": self.ssl_ciphers,
        }

class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

class ReverseProxyConfig:
    """Configuration for reverse proxy deployment"""
    
    def __init__(self):
        self.trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
        self.proxy_headers = os.getenv("PROXY_HEADERS", "X-Forwarded-For,X-Forwarded-Proto").split(",")
        self.forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
        
    def get_proxy_config(self) -> Dict[str, Any]:
        """Get proxy configuration for Uvicorn"""
        return {
            "proxy_headers": True,
            "forwarded_allow_ips": self.forwarded_allow_ips,
            "headers": [("server", "SplunkMCP")],
        }

# SSL Configuration generator
def generate_ssl_config() -> HTTPSConfig:
    """Generate SSL configuration"""
    return HTTPSConfig()

def get_security_headers() -> Dict[str, str]:
    """Get security headers"""
    return SecurityHeaders.get_security_headers()

def get_proxy_config() -> Dict[str, Any]:
    """Get reverse proxy configuration"""
    return ReverseProxyConfig().get_proxy_config()

# Example SSL certificate generation script
SSL_SETUP_SCRIPT = """
#!/bin/bash
# Generate self-signed SSL certificate for development
# DO NOT use in production!

CERT_DIR="./certs"
mkdir -p $CERT_DIR

# Generate private key
openssl genrsa -out $CERT_DIR/server.key 2048

# Generate certificate signing request
openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr \
    -subj "/C=US/ST=State/L=City