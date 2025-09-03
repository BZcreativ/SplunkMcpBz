#!/bin/bash
# SSL Certificate Setup Script for Splunk MCP Server
# Usage: ./setup_ssl.sh [production|development]

set -e

MODE=${1:-development}
CERT_DIR="./certs"
DOMAIN=${2:-localhost}

echo "Setting up SSL certificates for $MODE mode..."

# Create certificate directory
mkdir -p $CERT_DIR

case $MODE in
    "development")
        echo "Generating self-signed certificate for development..."
        
        # Generate private key
        openssl genrsa -out $CERT_DIR/server.key 2048
        
        # Generate certificate signing request
        openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr \
            -subj "/C=US/ST=Development/L=Local/O=SplunkMCP/CN=$DOMAIN"
        
        # Generate self-signed certificate
        openssl x509 -req -days 365 -in $CERT_DIR/server.csr \
            -signkey $CERT_DIR/server.key -out $CERT_DIR/server.crt
        
        # Clean up CSR
        rm $CERT_DIR/server.csr
        
        echo "Development certificates created:"
        echo "  Private key: $CERT_DIR/server.key"
        echo "  Certificate: $CERT_DIR/server.crt"
        echo ""
        echo "To use these certificates, set in your .env file:"
        echo "SSL_KEYFILE=$CERT_DIR/server.key"
        echo "SSL_CERTFILE=$CERT_DIR/server.crt"
        ;;
        
    "production")
        echo "Production SSL setup requires valid certificates from a CA."
        echo "Please obtain certificates from Let's Encrypt or your preferred CA."
        echo ""
        echo "Once you have your certificates, set in your .env file:"
        echo "SSL_KEYFILE=/path/to/your/private.key"
        echo "SSL_CERTFILE=/path/to/your/certificate.crt"
        echo "SSL_CA_CERTS=/path/to/ca-bundle.crt (optional)"
        ;;
        
    *)
        echo "Usage: $0 [development|production] [domain]"
        echo "  development: Generate self-signed certificates"
        echo "  production: Show instructions for production certificates"
        exit 1
        ;;
esac