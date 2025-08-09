# Splunk MCP Server

A Model Context Protocol (MCP) server for interacting with Splunk and Splunk ITSI.

## Overview

This project provides a set of tools for interacting with Splunk and Splunk ITSI via their REST APIs. The server is built with `fastmcp` and can be run in a Docker container.

## Features

### Redis Integration
The server now includes comprehensive Redis integration for:
- **Caching**: Splunk query results and ITSI data caching with TTL
- **Session Management**: User session storage and retrieval
- **Rate Limiting**: Distributed rate limiting using Redis
- **Task Queue**: Background task processing for long-running operations

### Splunk Tools
*   `search_splunk`: Execute a Splunk search query with optional caching
*   `list_indexes`: List all Splunk indexes
*   `list_saved_searches`: List all saved searches in the Splunk instance
*   `list_users`: List all Splunk users
*   `current_user`: Get information about the current user

### ITSI Tools (with Redis caching)
*   `get_itsi_services`: List all ITSI services with caching
*   `get_itsi_service_health`: Get health status with caching
*   `get_itsi_kpis`: Get ITSI KPIs with caching
*   `get_itsi_alerts`: Get ITSI alerts with caching
*   `get_itsi_entities`: Get ITSI service entities with caching
*   `get_itsi_entity_types`: Get ITSI entity types with caching
*   `get_itsi_glass_tables`: Get ITSI glass tables with caching
*   `get_itsi_service_analytics`: Get analytics for an ITSI service with caching

## Getting Started

### Prerequisites

*   Python 3.10+
*   Poetry
*   Docker

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd SplunkMCP
    ```

2.  Install dependencies:
    ```bash
    poetry install
    ```

3.  Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```

4.  Update the `.env` file with your Splunk connection details.

### Usage

#### Running the Server Locally
To run the server locally, use the following command:
```bash
poetry run python src/splunk_mcp/main.py
```

#### Running with Docker
To run the server with Docker, first build the image:
```bash
docker-compose build
```
Then, run the container:
```bash
docker-compose up
```
The server will be available at `http://localhost:8334`.

### Using the MCP Client
You can use the `fastmcp` client to interact with the server. Here is an example of how to call the `search_splunk` tool:

```python
import asyncio
from fastmcp import Client

async def main():
async with Client("http://localhost:8334") as client:
        result = await client.call_tool("search_splunk", {"query": "search index=_internal | head 1"})
        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
```

## Client Configuration

This server can be used with any MCP-compliant client, such as Cline, Claude, or Gemini. The server exposes an HTTP endpoint that clients can connect to.

### Connection Modes

*   **API (HTTP)**: Primary communication mode with dual endpoints:
  - `/mcp`: Standard MCP endpoint
  - `/sse`: Server-Sent Events endpoint
  The server listens on port `8000` inside Docker (mapped to `8334` on host)
*   **SSE (Server-Sent Events)**: Enhanced with keep-alive and protocol version headers
*   **Stdio**: For local, single-session tools (not primary interaction mode)
*   **Remote Server Connection**:
  ```
  ssh root@192.168.1.210
  su toto
  cd /home/toto/bzmcp/SplunkMcpBz
  ```

### Configuring a Client

To configure a client to use this server, you need to provide the server's URL and specify the root directory of the project. This allows the client to discover the server's tools and resources.

Here is an example configuration for an MCP client:

```json
{
  "servers": [
    {
      "name": "SplunkMCP",
      "protocol": "http",
      "url": "http://localhost:8334",
      "roots": [
        {
          "uri": "file:///path/to/your/SplunkMCP",
          "name": "SplunkMCP"
        }
      ]
    }
  ]
}
```

Replace `/path/to/your/SplunkMCP` with the absolute path to the `SplunkMCP` project directory on your local machine.

### Cline (VS Code) Configuration

To use this server with Cline in VS Code, you can add the server configuration to your `settings.json` file:

```json
"cline.mcp.servers": [
    {
        "name": "SplunkMCP",
        "protocol": "http",
        "url": "http://localhost:8334",
        "roots": [
            {
                "uri": "file:///path/to/your/SplunkMCP",
                "name": "SplunkMCP"
            }
        ]
    }
]
```

Make sure to replace `/path/to/your/SplunkMCP` with the correct path.

## Remote Docker Deployment

If you are running the Splunk MCP server in a Docker container on a remote machine, you will need to update the client configuration to point to the remote machine's IP address or hostname.

For example, if the remote machine's IP address is `192.168.1.100`, the client configuration would be:

```json
{
  "servers": [
    {
      "name": "SplunkMCP",
      "protocol": "http",
      "url": "http://192.168.1.100:8334",
      "roots": [
        {
          "uri": "file:///path/to/your/SplunkMCP",
          "name": "SplunkMCP"
        }
      ]
    }
  ]
}
```

Note that the `roots` URI should still point to the project directory on your **local** machine. This allows the client to manage and display the project context correctly, even when the server is running on a remote machine.

## Recent Updates

### [1.0.1] - 2025-07-12
#### Changed
- Updated default port from 8333 to 8334 to resolve conflicts

### [1.0.0] - 2025-07-11
#### Added
- Initial FastMCP server implementation
- Docker container support
- Health check endpoint (/health)
- MCP endpoint (/mcp) with basic tools:
  - get_server_info
  - list_indexes

#### Changed
- Simplified FastMCP initialization to use only required parameters
- Removed obsolete version field from docker-compose.yml
- Updated dependencies in requirements.txt

#### Fixed
- Resolved "Session terminated" connection issues
- Fixed port allocation conflicts
- Addressed FastMCP initialization errors

## Acknowledgements

This project is inspired by the [splunk-mcp](https://github.com/livehybrid/splunk-mcp) project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support & Donations

If you find this project useful, please consider supporting its development by making a donation.

[Your Donation Link Here]
