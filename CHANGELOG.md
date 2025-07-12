# Splunk MCP Server Changelog

## [1.0.1] - 2025-07-12
### Changed
- Updated default port from 8333 to 8334 to resolve conflicts

## [1.0.0] - 2025-07-11
### Added
- Initial FastMCP server implementation
- Docker container support
- Health check endpoint (/health)
- MCP endpoint (/mcp) with basic tools:
  - get_server_info
  - list_indexes

### Changed
- Simplified FastMCP initialization to use only required parameters
- Removed obsolete version field from docker-compose.yml
- Updated dependencies in requirements.txt

### Fixed
- Resolved "Session terminated" connection issues
- Fixed port allocation conflicts
- Addressed FastMCP initialization errors
