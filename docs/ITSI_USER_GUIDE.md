# Splunk ITSI Integration User Guide

## Overview

This guide provides documentation for using the Splunk ITSI (Intelligent Service Insights) integration with the Splunk MCP (Model Context Protocol) server. The integration allows you to interact with ITSI services, KPIs, alerts, and other ITSI components through MCP tools.

## Available Tools

The following ITSI tools are available through the MCP server:

### Service Management
- `get_itsi_services` - Retrieve ITSI services
- `get_itsi_service_health` - Get health status for a specific service
- `get_itsi_service_analytics` - Get analytics for an ITSI service

### KPI Management
- `get_itsi_kpis` - Retrieve ITSI KPIs
- `get_itsi_kpi_templates` - Get ITSI KPI templates

### Entity Management
- `get_itsi_entities` - Get ITSI service entities
- `get_itsi_entity_types` - Get ITSI entity types

### Alert and Event Management
- `get_itsi_alerts` - Retrieve ITSI alerts
- `get_itsi_notable_events` - Get ITSI notable events

### Visualization
- `get_itsi_glass_tables` - Get ITSI glass tables
- `get_itsi_deep_dives` - Get ITSI deep dives
- `get_itsi_home_views` - Get ITSI home views

### Operational Management
- `get_itsi_correlation_searches` - Get ITSI correlation searches
- `get_itsi_maintenance_calendars` - Get ITSI maintenance calendars
- `get_itsi_teams` - Get ITSI teams

## Usage Examples

### Getting All ITSI Services
```python
# Get all ITSI services
services = await get_itsi_services()
```

### Getting Health Status for a Specific Service
```python
# Get health status for a specific service
health = await get_itsi_service_health(service_name="my_service")
```

### Getting KPIs for a Service
```python
# Get KPIs for a specific service
kpis = await get_itsi_kpis(service_name="my_service")
```

### Getting Notable Events
```python
# Get notable events for the last 24 hours
events = await get_itsi_notable_events(time_range="-24h")

# Get notable events for a specific service
events = await get_itsi_notable_events(service_name="my_service", time_range="-7d")
```

## Authentication and Permissions

All ITSI tools require authentication and the `read:itsi` permission. Make sure your user has the appropriate permissions to access ITSI data.

## Error Handling

The tools will raise appropriate exceptions when errors occur:
- `SplunkQueryError` - For issues with Splunk queries
- `HTTPException` - For authentication and permission issues

## Configuration

Make sure your environment is properly configured with:
- SPLUNK_HOST - Your Splunk server hostname
- SPLUNK_PORT - Your Splunk server port (default: 8089)
- SPLUNK_SCHEME - Connection scheme (default: https)
- SPLUNK_TOKEN - Your Splunk authentication token

## Troubleshooting

If you encounter issues:
1. Verify your Splunk connection settings
2. Check that your user has the necessary permissions
3. Ensure ITSI is properly installed and configured in your Splunk instance
4. Review the server logs for detailed error information

## Support

For support or to report issues, please refer to the project's GitHub repository or contact the development team.

---

*This guide is part of the Splunk MCP server documentation.*