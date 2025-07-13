# Splunk MCP Server

A Model Context Protocol (MCP) server for interacting with Splunk and Splunk ITSI.

## Overview

This project provides a set of tools for interacting with Splunk and Splunk ITSI via their REST APIs. The server is built with `fastmcp` and can be run in a Docker container.

## Features

### Splunk Tools
*   `search_splunk`: Execute a Splunk search query.
*   `list_indexes`: List all Splunk indexes.
*   `list_saved_searches`: List all saved searches in the Splunk instance.
*   `list_users`: List all Splunk users.
*   `current_user`: Get information about the current user.

### ITSI Tools
*   `list_itsi_services`: List all ITSI services.
*   `get_itsi_service`: Get a specific ITSI service by its ID.
*   `create_itsi_service`: Create a new ITSI service.
*   `delete_itsi_service`: Delete a specific ITSI service by its ID.
*   `list_itsi_entity_types`: List all ITSI entity types.
*   `get_itsi_entity_type`: Get a specific ITSI entity type by its ID.
*   `create_itsi_entity_type`: Create a new ITSI entity type.
*   `delete_itsi_entity_type`: Delete a specific ITSI entity type by its ID.
*   `list_itsi_entities`: List all ITSI entities.
*   `get_itsi_entity`: Get a specific ITSI entity by its ID.
*   `create_itsi_entity`: Create a new ITSI entity.
*   `delete_itsi_entity`: Delete a specific ITSI entity by its ID.
*   `list_itsi_service_templates`: List all ITSI service templates.
*   `get_itsi_service_template`: Get a specific ITSI service template by its ID.
*   `create_itsi_service_template`: Create a new ITSI service template.
*   `delete_itsi_service_template`: Delete a specific ITSI service template by its ID.
*   `list_itsi_deep_dives`: List all ITSI deep dives.
*   `get_itsi_deep_dive`: Get a specific ITSI deep dive by its ID.
*   `create_itsi_deep_dive`: Create a new ITSI deep dive.
*   `delete_itsi_deep_dive`: Delete a specific ITSI deep dive by its ID.
*   `list_itsi_glass_tables`: List all ITSI glass tables.
*   `get_itsi_glass_table`: Get a specific ITSI glass table by its ID.
*   `create_itsi_glass_table`: Create a new ITSI glass table.
*   `delete_itsi_glass_table`: Delete a specific ITSI glass table by its ID.
*   `list_itsi_home_views`: List all ITSI home views.
*   `get_itsi_home_view`: Get a specific ITSI home view by its ID.
*   `create_itsi_home_view`: Create a new ITSI home view.
*   `delete_itsi_home_view`: Delete a specific ITSI home view by its ID.
*   `list_itsi_kpi_templates`: List all ITSI KPI templates.
*   `get_itsi_kpi_template`: Get a specific ITSI KPI template by its ID.
*   `create_itsi_kpi_template`: Create a new ITSI KPI template.
*   `delete_itsi_kpi_template`: Delete a specific ITSI KPI template by its ID.
*   `list_itsi_kpi_threshold_templates`: List all ITSI KPI threshold templates.
*   `get_itsi_kpi_threshold_template`: Get a specific ITSI KPI threshold template by its ID.
*   `create_itsi_kpi_threshold_template`: Create a new ITSI KPI threshold template.
*   `delete_itsi_kpi_threshold_template`: Delete a specific ITSI KPI threshold template by its ID.
*   `list_itsi_kpi_base_searches`: List all ITSI KPI base searches.
*   `get_itsi_kpi_base_search`: Get a specific ITSI KPI base search by its ID.
*   `create_itsi_kpi_base_search`: Create a new ITSI KPI base search.
*   `delete_itsi_kpi_base_search`: Delete a specific ITSI KPI base search by its ID.
*   `list_itsi_notable_events`: List all ITSI notable events.
*   `get_itsi_notable_event`: Get a specific ITSI notable event by its ID.
*   `create_itsi_notable_event`: Create a new ITSI notable event.
*   `delete_itsi_notable_event`: Delete a specific ITSI notable event by its ID.
*   `list_itsi_correlation_searches`: List all ITSI correlation searches.
*   `get_itsi_correlation_search`: Get a specific ITSI correlation search by its ID.
*   `create_itsi_correlation_search`: Create a new ITSI correlation search.
*   `delete_itsi_correlation_search`: Delete a specific ITSI correlation search by its ID.
*   `list_itsi_maintenance_calendars`: List all ITSI maintenance calendars.
*   `get_itsi_maintenance_calendar`: Get a specific ITSI maintenance calendar by its ID.
*   `create_itsi_maintenance_calendar`: Create a new ITSI maintenance calendar.
*   `delete_itsi_maintenance_calendar`: Delete a specific ITSI maintenance calendar by its ID.
*   `list_itsi_teams`: List all ITSI teams.
*   `get_itsi_team`: Get a specific ITSI team by its ID.
*   `create_itsi_team`: Create a new ITSI team.
*   `delete_itsi_team`: Delete a specific ITSI team by its ID.

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
