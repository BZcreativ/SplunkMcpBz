import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP
from splunk_mcp.splunk_connector import SplunkConnector
from splunk_mcp.itsi_connector import ITSIConnector
import json

from fastapi import FastAPI

mcp_server = FastMCP("SplunkMCP")
# Create a FastAPI app
app = FastAPI()

# Mount the FastMCP application at the /mcp path
app.mount("/mcp", mcp_server.http_app())

# Add a simple root endpoint for testing server accessibility
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@mcp_server.tool()
async def search_splunk(query: str, earliest: str = "-15m", latest: str = "now", max_results: int = 1000) -> str:
    """Execute a Splunk search query"""
    try:
        connector = SplunkConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to Splunk"

        job = service.jobs.create(query, earliest_time=earliest, latest_time=latest)
        results = job.results(count=max_results)
        return str(results)
    except Exception as e:
        return f"Error executing search: {e}"

@mcp_server.tool()
async def list_indexes() -> str:
    """List all Splunk indexes"""
    try:
        connector = SplunkConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to Splunk"

        indexes = service.indexes
        index_list = [index.name for index in indexes]
        return str(index_list)
    except Exception as e:
        return f"Error listing indexes: {e}"

@mcp_server.tool()
async def list_saved_searches() -> str:
    """List all saved searches in the Splunk instance"""
    try:
        connector = SplunkConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to Splunk"

        saved_searches = service.saved_searches
        search_list = [s.name for s in saved_searches]
        return str(search_list)
    except Exception as e:
        return f"Error listing saved searches: {e}"

@mcp_server.tool()
async def list_users() -> str:
    """List all Splunk users"""
    try:
        connector = SplunkConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to Splunk"

        users = service.users
        user_list = [user.name for user in users]
        return str(user_list)
    except Exception as e:
        return f"Error listing users: {e}"

@mcp_server.tool()
async def current_user() -> str:
    """Get information about the current user"""
    try:
        connector = SplunkConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to Splunk"

        return str(service.username)
    except Exception as e:
        return f"Error getting current user: {e}"

@mcp_server.tool()
async def list_itsi_services() -> str:
    """List all ITSI services"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        # ITSI services are stored in a KV store collection.
        response = service.get('storage/collections/data/itsi_services')
        data = json.loads(response.body.read())
        service_list = [item.get('title', item.get('_key')) for item in data]
        return str(service_list)
    except Exception as e:
        return f"Error listing ITSI services: {e}"

@mcp_server.tool()
async def list_kv_store_collections() -> str:
    """List all KV store collections"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        collections = service.kvstore
        collection_list = [c.name for c in collections]
        return str(collection_list)
    except Exception as e:
        return f"Error listing KV store collections: {e}"

@mcp_server.tool()
async def get_itsi_service(service_id: str) -> str:
    """Get a specific ITSI service by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_services/{service_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI service: {e}"

@mcp_server.tool()
async def create_itsi_service(title: str, description: str) -> str:
    """Create a new ITSI service"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_services', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI service: {e}"

@mcp_server.tool()
async def delete_itsi_service(service_id: str) -> str:
    """Delete a specific ITSI service by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_services/{service_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI service: {e}"

@mcp_server.tool()
async def get_itsi_entity_type(entity_type_id: str) -> str:
    """Get a specific ITSI entity type by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_entity_type/{entity_type_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI entity type: {e}"

@mcp_server.tool()
async def list_itsi_entity_types() -> str:
    """List all ITSI entity types"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_entity_type')
        data = json.loads(response.body.read())
        entity_type_list = [item.get('title', item.get('_key')) for item in data]
        return str(entity_type_list)
    except Exception as e:
        return f"Error listing ITSI entity types: {e}"

@mcp_server.tool()
async def create_itsi_entity_type(title: str, description: str) -> str:
    """Create a new ITSI entity type"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_entity_type', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI entity type: {e}"

@mcp_server.tool()
async def delete_itsi_entity_type(entity_type_id: str) -> str:
    """Delete a specific ITSI entity type by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_entity_type/{entity_type_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI entity type: {e}"

# ITSI Entity Tools
@mcp_server.tool()
async def list_itsi_entities() -> str:
    """List all ITSI entities"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_services')
        data = json.loads(response.body.read())
        entity_list = [item.get('title', item.get('_key')) for item in data]
        return str(entity_list)
    except Exception as e:
        return f"Error listing ITSI entities: {e}"

@mcp_server.tool()
async def get_itsi_entity(entity_id: str) -> str:
    """Get a specific ITSI entity by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_services/{entity_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI entity: {e}"

@mcp_server.tool()
async def create_itsi_entity(title: str, description: str) -> str:
    """Create a new ITSI entity"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_services', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI entity: {e}"

@mcp_server.tool()
async def delete_itsi_entity(entity_id: str) -> str:
    """Delete a specific ITSI entity by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_services/{entity_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI entity: {e}"

# ITSI Service Template Tools
@mcp_server.tool()
async def list_itsi_service_templates() -> str:
    """List all ITSI service templates"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_base_service_template')
        data = json.loads(response.body.read())
        template_list = [item.get('title', item.get('_key')) for item in data]
        return str(template_list)
    except Exception as e:
        return f"Error listing ITSI service templates: {e}"

@mcp_server.tool()
async def get_itsi_service_template(template_id: str) -> str:
    """Get a specific ITSI service template by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_base_service_template/{template_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI service template: {e}"

@mcp_server.tool()
async def create_itsi_service_template(title: str, description: str) -> str:
    """Create a new ITSI service template"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_base_service_template', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI service template: {e}"

@mcp_server.tool()
async def delete_itsi_service_template(template_id: str) -> str:
    """Delete a specific ITSI service template by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_base_service_template/{template_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI service template: {e}"

# ITSI Deep Dive Tools
@mcp_server.tool()
async def list_itsi_deep_dives() -> str:
    """List all ITSI deep dives"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/SA-ITOA_files')
        data = json.loads(response.body.read())
        deep_dive_list = [item.get('title', item.get('_key')) for item in data]
        return str(deep_dive_list)
    except Exception as e:
        return f"Error listing ITSI deep dives: {e}"

@mcp_server.tool()
async def get_itsi_deep_dive(deep_dive_id: str) -> str:
    """Get a specific ITSI deep dive by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/SA-ITOA_files/{deep_dive_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI deep dive: {e}"

@mcp_server.tool()
async def create_itsi_deep_dive(title: str, description: str) -> str:
    """Create a new ITSI deep dive"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/SA-ITOA_files', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI deep dive: {e}"

@mcp_server.tool()
async def delete_itsi_deep_dive(deep_dive_id: str) -> str:
    """Delete a specific ITSI deep dive by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/SA-ITOA_files/{deep_dive_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI deep dive: {e}"

# ITSI Glass Table Tools
@mcp_server.tool()
async def list_itsi_glass_tables() -> str:
    """List all ITSI glass tables"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/SA-ITOA_files')
        data = json.loads(response.body.read())
        table_list = [item.get('title', item.get('_key')) for item in data]
        return str(table_list)
    except Exception as e:
        return f"Error listing ITSI glass tables: {e}"

@mcp_server.tool()
async def get_itsi_glass_table(table_id: str) -> str:
    """Get a specific ITSI glass table by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/SA-ITOA_files/{table_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI glass table: {e}"

@mcp_server.tool()
async def create_itsi_glass_table(title: str, description: str) -> str:
    """Create a new ITSI glass table"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/SA-ITOA_files', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI glass table: {e}"

@mcp_server.tool()
async def delete_itsi_glass_table(table_id: str) -> str:
    """Delete a specific ITSI glass table by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/SA-ITOA_files/{table_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI glass table: {e}"

# ITSI Home View Tools
@mcp_server.tool()
async def list_itsi_home_views() -> str:
    """List all ITSI home views"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_service_analyzer')
        data = json.loads(response.body.read())
        view_list = [item.get('title', item.get('_key')) for item in data]
        return str(view_list)
    except Exception as e:
        return f"Error listing ITSI home views: {e}"

@mcp_server.tool()
async def get_itsi_home_view(view_id: str) -> str:
    """Get a specific ITSI home view by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_service_analyzer/{view_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI home view: {e}"

@mcp_server.tool()
async def create_itsi_home_view(title: str, description: str) -> str:
    """Create a new ITSI home view"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_service_analyzer', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI home view: {e}"

@mcp_server.tool()
async def delete_itsi_home_view(view_id: str) -> str:
    """Delete a specific ITSI home view by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_service_analyzer/{view_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI home view: {e}"

# ITSI KPI Template Tools
@mcp_server.tool()
async def list_itsi_kpi_templates() -> str:
    """List all ITSI KPI templates"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_kpi_at_info')
        data = json.loads(response.body.read())
        template_list = [item.get('title', item.get('_key')) for item in data]
        return str(template_list)
    except Exception as e:
        return f"Error listing ITSI KPI templates: {e}"

@mcp_server.tool()
async def get_itsi_kpi_template(template_id: str) -> str:
    """Get a specific ITSI KPI template by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_kpi_at_info/{template_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI KPI template: {e}"

@mcp_server.tool()
async def create_itsi_kpi_template(title: str, description: str) -> str:
    """Create a new ITSI KPI template"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_kpi_at_info', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI KPI template: {e}"

@mcp_server.tool()
async def delete_itsi_kpi_template(template_id: str) -> str:
    """Delete a specific ITSI KPI template by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_kpi_at_info/{template_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI KPI template: {e}"

# ITSI KPI Threshold Template Tools
@mcp_server.tool()
async def list_itsi_kpi_threshold_templates() -> str:
    """List all ITSI KPI threshold templates"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_entity_thresholds')
        data = json.loads(response.body.read())
        template_list = [item.get('title', item.get('_key')) for item in data]
        return str(template_list)
    except Exception as e:
        return f"Error listing ITSI KPI threshold templates: {e}"

@mcp_server.tool()
async def get_itsi_kpi_threshold_template(template_id: str) -> str:
    """Get a specific ITSI KPI threshold template by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_entity_thresholds/{template_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI KPI threshold template: {e}"

@mcp_server.tool()
async def create_itsi_kpi_threshold_template(title: str, description: str) -> str:
    """Create a new ITSI KPI threshold template"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_entity_thresholds', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI KPI threshold template: {e}"

@mcp_server.tool()
async def delete_itsi_kpi_threshold_template(template_id: str) -> str:
    """Delete a specific ITSI KPI threshold template by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_entity_thresholds/{template_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI KPI threshold template: {e}"

# ITSI KPI Base Search Tools
@mcp_server.tool()
async def list_itsi_kpi_base_searches() -> str:
    """List all ITSI KPI base searches"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_kpi_at_info')
        data = json.loads(response.body.read())
        search_list = [item.get('title', item.get('_key')) for item in data]
        return str(search_list)
    except Exception as e:
        return f"Error listing ITSI KPI base searches: {e}"

@mcp_server.tool()
async def get_itsi_kpi_base_search(search_id: str) -> str:
    """Get a specific ITSI KPI base search by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_kpi_at_info/{search_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI KPI base search: {e}"

@mcp_server.tool()
async def create_itsi_kpi_base_search(title: str, description: str) -> str:
    """Create a new ITSI KPI base search"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_kpi_at_info', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI KPI base search: {e}"

@mcp_server.tool()
async def delete_itsi_kpi_base_search(search_id: str) -> str:
    """Delete a specific ITSI KPI base search by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_kpi_at_info/{search_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI KPI base search: {e}"

# ITSI Notable Event Tools
@mcp_server.tool()
async def list_itsi_notable_events() -> str:
    """List all ITSI notable events"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_notable_event_state')
        data = json.loads(response.body.read())
        event_list = [item.get('title', item.get('_key')) for item in data]
        return str(event_list)
    except Exception as e:
        return f"Error listing ITSI notable events: {e}"

@mcp_server.tool()
async def get_itsi_notable_event(event_id: str) -> str:
    """Get a specific ITSI notable event by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_notable_event_state/{event_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI notable event: {e}"

@mcp_server.tool()
async def create_itsi_notable_event(title: str, description: str) -> str:
    """Create a new ITSI notable event"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_notable_event_state', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI notable event: {e}"

@mcp_server.tool()
async def delete_itsi_notable_event(event_id: str) -> str:
    """Delete a specific ITSI notable event by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_notable_event_state/{event_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI notable event: {e}"

# ITSI Correlation Search Tools
@mcp_server.tool()
async def list_itsi_correlation_searches() -> str:
    """List all ITSI correlation searches"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_correlation_engine_group_template')
        data = json.loads(response.body.read())
        search_list = [item.get('title', item.get('_key')) for item in data]
        return str(search_list)
    except Exception as e:
        return f"Error listing ITSI correlation searches: {e}"

@mcp_server.tool()
async def get_itsi_correlation_search(search_id: str) -> str:
    """Get a specific ITSI correlation search by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_correlation_engine_group_template/{search_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI correlation search: {e}"

@mcp_server.tool()
async def create_itsi_correlation_search(title: str, description: str) -> str:
    """Create a new ITSI correlation search"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_correlation_engine_group_template', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI correlation search: {e}"

@mcp_server.tool()
async def delete_itsi_correlation_search(search_id: str) -> str:
    """Delete a specific ITSI correlation search by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_correlation_engine_group_template/{search_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI correlation search: {e}"

# ITSI Maintenance Calendar Tools
@mcp_server.tool()
async def list_itsi_maintenance_calendars() -> str:
    """List all ITSI maintenance calendars"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/maintenance_calendar')
        data = json.loads(response.body.read())
        calendar_list = [item.get('title', item.get('_key')) for item in data]
        return str(calendar_list)
    except Exception as e:
        return f"Error listing ITSI maintenance calendars: {e}"

@mcp_server.tool()
async def get_itsi_maintenance_calendar(calendar_id: str) -> str:
    """Get a specific ITSI maintenance calendar by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/maintenance_calendar/{calendar_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI maintenance calendar: {e}"

@mcp_server.tool()
async def create_itsi_maintenance_calendar(title: str, description: str) -> str:
    """Create a new ITSI maintenance calendar"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/maintenance_calendar', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI maintenance calendar: {e}"

@mcp_server.tool()
async def delete_itsi_maintenance_calendar(calendar_id: str) -> str:
    """Delete a specific ITSI maintenance calendar by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/maintenance_calendar/{calendar_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI maintenance calendar: {e}"

# ITSI Team Tools
@mcp_server.tool()
async def list_itsi_teams() -> str:
    """List all ITSI teams"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get('storage/collections/data/itsi_team')
        data = json.loads(response.body.read())
        team_list = [item.get('title', item.get('_key')) for item in data]
        return str(team_list)
    except Exception as e:
        return f"Error listing ITSI teams: {e}"

@mcp_server.tool()
async def get_itsi_team(team_id: str) -> str:
    """Get a specific ITSI team by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.get(f'storage/collections/data/itsi_team/{team_id}')
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error getting ITSI team: {e}"

@mcp_server.tool()
async def create_itsi_team(title: str, description: str) -> str:
    """Create a new ITSI team"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.post('storage/collections/data/itsi_team', headers=[('Content-Type', 'application/json')], body=json.dumps({"title": title, "description": description}))
        data = json.loads(response.body.read())
        return str(data)
    except Exception as e:
        return f"Error creating ITSI team: {e}"

@mcp_server.tool()
async def delete_itsi_team(team_id: str) -> str:
    """Delete a specific ITSI team by its ID"""
    try:
        connector = ITSIConnector()
        service = connector.connect()
        if not service:
            return "Error: Could not connect to ITSI"

        response = service.delete(f'storage/collections/data/itsi_team/{team_id}')
        return str(response.status)
    except Exception as e:
        return f"Error deleting ITSI team: {e}"

# Remove the direct run call when using Uvicorn
