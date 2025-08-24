# Splunk MCP Server

A comprehensive Model Context Protocol (MCP) server for Splunk integration with advanced ITSI (IT Service Intelligence) capabilities, Redis caching, and security features.

## 🚀 Features

- **Splunk Integration**: Full Splunk REST API integration with search capabilities
- **ITSI Support**: Complete IT Service Intelligence operations
- **Redis Caching**: High-performance caching with session management and rate limiting
- **Security**: JWT authentication, role-based access control, and security middleware
- **Docker Support**: Containerized deployment with Docker Compose
- **Health Monitoring**: Comprehensive health checks and diagnostics
- **Rate Limiting**: Distributed rate limiting with Redis backend

## 📁 Project Structure

```
SplunkMcpBz/
├── src/
│   └── splunk_mcp/
│       ├── main.py                 # Main MCP server
│       ├── redis_manager.py        # Redis integration
│       ├── itsi_helper_with_cache.py # ITSI with caching
│       ├── itsi_helper.py          # ITSI operations
│       ├── itsi_full_helper.py     # Extended ITSI features
│       ├── itsi_connector.py       # ITSI connection
│       ├── splunk_connector.py     # Splunk connection
│       ├── auth_middleware.py      # Authentication
│       ├── security.py             # Security features
│       └── search_helper.py        # Search utilities
├── tests/
│   ├── integration/               # Integration tests
│   ├── unit/                      # Unit tests
│   └── test_mcp_client.py         # MCP client tests
├── docs/                          # Documentation
├── examples/                      # Usage examples
├── scripts/                       # Utility scripts
├── config/                        # Configuration files
├── docker-compose.yml            # Docker Compose
├── Dockerfile                    # Docker image
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Poetry configuration
└── README.md                    # This file
```

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for local development)
- Splunk instance with REST API access
- Redis (included in Docker Compose)

### Docker Deployment

```bash
# Clone the repository
git clone https://github.com/BZcreativ/SplunkMcpBz.git
cd SplunkMcpBz

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
# or
poetry install

# Run tests
pytest tests/

# Start server
python -m src.splunk_mcp.main
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Splunk Configuration
SPLUNK_HOST=your-splunk-host
SPLUNK_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-password

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Security
JWT_SECRET_KEY=your-secret-key
```

### Docker Compose Services

- **mcp-server**: Main MCP server (port 8334)
- **redis**: Redis cache and session store (port 6379)

## 🔍 API Endpoints

### Health Check
- `GET /api/health` - Server health status
- `GET /api/health/redis` - Redis connection status

### MCP Tools

#### Core Splunk Tools
- `search_splunk` - Execute Splunk searches
- `get_server_info` - Get Splunk server information
- `list_indexes` - List available Splunk indexes

#### ITSI Tools (15 Total)
**Core ITSI Operations:**
- `get_itsi_services` - List and manage ITSI services
- `get_itsi_service_health` - Get health status for specific services
- `get_itsi_kpis` - Get service KPIs and metrics
- `get_itsi_alerts` - Retrieve ITSI alerts and notifications
- `get_itsi_entities` - Manage ITSI service entities
- `get_itsi_entity_types` - Get ITSI entity type definitions
- `get_itsi_glass_tables` - Access ITSI glass table views
- `get_itsi_service_analytics` - Get service analytics and trends

**Enhanced ITSI Features (New in v2.1.0):**
- `get_itsi_deep_dives` - ITSI deep dive analysis and investigations
- `get_itsi_home_views` - Home view configuration management
- `get_itsi_kpi_templates` - KPI template system integration
- `get_itsi_notable_events` - Notable event tracking with time filtering
- `get_itsi_correlation_searches` - Correlation search management
- `get_itsi_maintenance_calendars` - Maintenance calendar scheduling
- `get_itsi_teams` - Team management and collaboration

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Integration Tests
```bash
pytest tests/integration/
```

### ITSI Integration Tests (New in v2.1.0)
```bash
# Simple ITSI functionality test
python scripts/test_itsi_simple.py

# Enhanced ITSI integration test
python scripts/test_enhanced_itsi.py

# ITSI helper function validation
python scripts/test_itsi_helper_functions.py
```

### Redis Integration Test
```bash
python tests/integration/test_redis_integration.py
```

### Deployment Testing
```bash
# Test deployment to remote server
python scripts/deploy_to_remote.py
```

## 📊 Redis Features

### Caching
- **Query Caching**: Splunk search results cached for 5 minutes
- **ITSI Data**: Service and KPI data cached for 60 seconds
- **Session Storage**: User sessions with 1-hour TTL

### Rate Limiting
- **Distributed**: Works across multiple server instances
- **Configurable**: Per-endpoint rate limits
- **Sliding Window**: Accurate rate limiting

### Session Management
- **Persistent**: Survives server restarts
- **Scalable**: Works with load balancers
- **Secure**: Encrypted session data

## 🔐 Security Features

- JWT-based authentication
- Role-based access control
- Request rate limiting
- Input validation
- Security headers
- Audit logging

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   docker-compose exec redis redis-cli ping
   ```

2. **Splunk Connection Issues**
   ```bash
   python scripts/debug_client.py
   ```

3. **Health Check**
   ```bash
   curl http://localhost:8334/api/health
   ```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m src.splunk_mcp.main
```

## 📈 Performance

- **Caching**: 90% cache hit rate for repeated queries
- **Rate Limiting**: Prevents API abuse
- **Connection Pooling**: Efficient Redis connections
- **Async Processing**: Non-blocking operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- [Issues](https://github.com/BZcreativ/SplunkMcpBz/issues)
- [Discussions](https://github.com/BZcreativ/SplunkMcpBz/discussions)
- [Wiki](https://github.com/BZcreativ/SplunkMcpBz/wiki)