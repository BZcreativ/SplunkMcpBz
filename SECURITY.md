# Security Documentation - Splunk MCP Server

## Overview
This document provides comprehensive security documentation for the Splunk MCP server, including authentication, authorization, and security best practices.

## Security Features

### 1. Authentication
- **JWT Token-based Authentication**: Uses JSON Web Tokens for secure authentication
- **Token Expiry**: Configurable token expiration (default: 24 hours)
- **Token Refresh**: Support for token refresh without re-authentication
- **Rate Limiting**: Prevents brute force attacks on login endpoints

### 2. Authorization
- **Role-Based Access Control (RBAC)**: Three predefined roles with specific permissions
- **Permission-based Access**: Fine-grained permissions for each MCP tool
- **API Endpoint Protection**: All sensitive endpoints require authentication

### 3. Security Headers
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables XSS protection
- **Strict-Transport-Security**: Enforces HTTPS
- **Content-Security-Policy**: Restricts resource loading
- **Referrer-Policy**: Controls referrer information

### 4. Input Validation
- **SQL Injection Prevention**: Validates queries for dangerous patterns
- **XSS Prevention**: Sanitizes input data
- **Query Validation**: Validates Splunk queries for security

### 5. Rate Limiting
- **Per-user rate limiting**: Limits requests per user
- **Configurable limits**: Adjustable via environment variables
- **Rate limit headers**: Provides remaining request information

## User Roles and Permissions

### Admin Role
- **Permissions**: `read:*`, `write:*`, `delete:*`, `create:*`, `itsi:*`, `search:*`, `config:*`
- **Access**: Full access to all MCP tools and API endpoints

### User Role
- **Permissions**: `read:itsi`, `read:search`, `write:itsi`, `create:itsi`, `delete:itsi`
- **Access**: Standard ITSI and search operations

### Readonly Role
- **Permissions**: `read:itsi`, `read:search`
- **Access**: Read-only access to ITSI and search data

## API Endpoints

### Public Endpoints
- `GET /api/health` - Health check (no authentication required)

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Get current user info

### Protected Endpoints
- `GET /api/metrics` - System metrics (admin only)
- `GET /api/test-splunk-connection` - Test Splunk connection (authenticated users)

### MCP Tools (All require authentication)
- `GET /mcp/mcp_health_check` - Health check
- `GET /mcp/list_indexes` - List Splunk indexes
- `POST /mcp/splunk_search` - Execute Splunk search
- `GET /mcp/get_itsi_services` - Get ITSI services
- `GET /mcp/get_itsi_service_health` - Get service health
- `GET /mcp/get_itsi_kpis` - Get KPIs
- `GET /mcp/get_itsi_alerts` - Get alerts
- `GET /mcp/get_itsi_entities` - Get entities
- `GET /mcp/get_itsi_entity_types` - Get entity types
- `GET /mcp/get_itsi_glass_tables` - Get glass tables
- `GET /mcp/get_itsi_service_analytics` - Get service analytics

## Environment Variables

### Security Configuration
```bash
# Required
SECRET_KEY=your-secret-key-change-this-in-production

# Optional (with defaults)
TOKEN_EXPIRY_HOURS=24
MAX_REQUESTS_PER_MINUTE=100
ALLOWED_ORIGINS=*
VERIFY_SSL=false
```

### SSL Configuration (Optional)
```bash
SSL_KEYFILE=/path/to/ssl.key
SSL_CERTFILE=/path/to/ssl.crt
```

## Default Users

### Admin User
- **Username**: admin
- **Password**: admin123
- **Role**: admin

### Standard User
- **Username**: user
- **Password**: user123
- **Role**: user

### Readonly User
- **Username**: readonly
- **Password**: readonly123
- **Role**: readonly

## Usage Examples

### 1. Authentication
```bash
# Login
curl -X POST http://localhost:8334/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "admin",
  "roles": ["admin"]
}
```

### 2. Using MCP Tools
```bash
# With authentication
curl -X GET http://localhost:8334/mcp/list_indexes \
  -H "Authorization: Bearer YOUR_TOKEN"

# Without authentication (will fail)
curl -X GET http://localhost:8334/mcp/list_indexes
# Response: 401 Unauthorized
```

### 3. Testing Connection
```bash
# Test Splunk connection (requires auth)
curl -X GET http://localhost:8334/api/test-splunk-connection \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Security Best Practices

### 1. Production Deployment
- **Change default passwords** immediately
- **Use strong SECRET_KEY** (minimum 32 characters)
- **Enable SSL/TLS** for production
- **Configure ALLOWED_ORIGINS** appropriately
- **Set up proper logging** and monitoring

### 2. Token Management
- **Store tokens securely** on client side
- **Implement token rotation** for long-lived sessions
- **Monitor token usage** for anomalies
- **Set appropriate token expiry**

### 3. Network Security
- **Use HTTPS** in production
- **Configure firewall rules**
- **Use reverse proxy** (nginx/Apache)
- **Enable rate limiting**

### 4. Monitoring
- **Monitor authentication logs**
- **Track failed login attempts**
- **Set up alerts** for security events
- **Regular security audits**

## Testing Security

### Run Security Tests
```bash
# Start the server
python -m splunk_mcp.main

# Run security tests
python test_security_integration.py
```

### Manual Testing
```bash
# Test health endpoint (public)
curl http://localhost:8334/api/health

# Test protected endpoint without auth
curl http://localhost:8334/api/metrics
# Expected: 401 Unauthorized

# Test with valid auth
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8334/api/metrics
```

## Security Logging

### Log Levels
- **INFO**: Authentication successes, authorization checks
- **WARNING**: Rate limit violations, security events
- **ERROR**: Authentication failures, authorization failures

### Log Format
```json
{
  "event": "authentication",
  "user_id": "admin",
  "success": true,
  "ip": "192.168.1.100",
  "timestamp": "2024-07-14T21:30:00Z"
}
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check token validity
   - Verify token format (Bearer prefix)
   - Check token expiry

2. **403 Forbidden**
   - Verify user permissions
   - Check role assignments
   - Review permission requirements

3. **429 Too Many Requests**
   - Wait for rate limit reset
   - Check rate limit configuration
   - Implement request throttling

### Debug Mode
Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## Security Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure ALLOWED_ORIGINS
- [ ] Enable SSL/TLS
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Review user permissions
- [ ] Test security features
- [ ] Set up log rotation
- [ ] Configure firewall rules

## Support

For security issues or questions:
1. Check this documentation
2. Review security logs
3. Test with provided scripts
4. Contact system administrator
