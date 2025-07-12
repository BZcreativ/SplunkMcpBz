import pytest
from fastmcp import Client
from splunk_mcp.main import mcp_server

@pytest.mark.asyncio
async def test_search_splunk():
    async with Client(mcp_server) as client:
        result = await client.call_tool("search_splunk", {"query": "search index=_internal | head 1"})
        assert "Error executing search" not in result.data

@pytest.mark.asyncio
async def test_list_indexes():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_indexes")
        assert "Error listing indexes" not in result.data

@pytest.mark.asyncio
async def test_list_saved_searches():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_saved_searches")
        assert "Error listing saved searches" not in result.data

@pytest.mark.asyncio
async def test_list_users():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_users")
        assert "Error listing users" not in result.data

@pytest.mark.asyncio
async def test_current_user():
    async with Client(mcp_server) as client:
        result = await client.call_tool("current_user")
        assert "Error getting current user" not in result.data

@pytest.mark.asyncio
async def test_list_itsi_services():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_services")
        assert "Error listing ITSI services" not in result.data

@pytest.mark.asyncio
async def test_list_kv_store_collections():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_kv_store_collections")
        print(result.data)
        assert "Error listing KV store collections" not in result.data

@pytest.mark.asyncio
async def test_list_itsi_entity_types():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_entity_types")
        assert "Error listing ITSI entity types" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_entity_type():
    async with Client(mcp_server) as client:
        # Create a test entity type
        create_result = await client.call_tool("create_itsi_entity_type", {"title": "Test Entity Type", "description": "A test entity type"})
        assert "Error creating ITSI entity type" not in create_result.data
        entity_type_data = eval(create_result.data)
        entity_type_id = entity_type_data["_key"]

        # Get the entity type by ID
        get_result = await client.call_tool("get_itsi_entity_type", {"entity_type_id": entity_type_id})
        assert "Error getting ITSI entity type" not in get_result.data
        
        # Delete the test entity type
        delete_result = await client.call_tool("delete_itsi_entity_type", {"entity_type_id": entity_type_id})
        assert "Error deleting ITSI entity type" not in delete_result.data

@pytest.mark.asyncio
async def test_get_itsi_service():
    async with Client(mcp_server) as client:
        # Create a test service
        create_result = await client.call_tool("create_itsi_service", {"title": "Test Service", "description": "A test service"})
        assert "Error creating ITSI service" not in create_result.data
        service_data = eval(create_result.data)
        service_id = service_data["_key"]

        # Get the service by ID
        get_result = await client.call_tool("get_itsi_service", {"service_id": service_id})
        assert "Error getting ITSI service" not in get_result.data
        
        # Delete the test service
        delete_result = await client.call_tool("delete_itsi_service", {"service_id": service_id})
        assert "Error deleting ITSI service" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_entities():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_entities")
        assert "Error listing ITSI entities" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_entity():
    async with Client(mcp_server) as client:
        # Create a test entity
        create_result = await client.call_tool("create_itsi_entity", {"title": "Test Entity", "description": "A test entity"})
        assert "Error creating ITSI entity" not in create_result.data
        entity_data = eval(create_result.data)
        entity_id = entity_data["_key"]

        # Get the entity by ID
        get_result = await client.call_tool("get_itsi_entity", {"entity_id": entity_id})
        assert "Error getting ITSI entity" not in get_result.data
        
        # Delete the test entity
        delete_result = await client.call_tool("delete_itsi_entity", {"entity_id": entity_id})
        assert "Error deleting ITSI entity" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_service_templates():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_service_templates")
        assert "Error listing ITSI service templates" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_service_template():
    async with Client(mcp_server) as client:
        # Create a test service template
        create_result = await client.call_tool("create_itsi_service_template", {"title": "Test Service Template", "description": "A test service template"})
        assert "Error creating ITSI service template" not in create_result.data
        template_data = eval(create_result.data)
        template_id = template_data["_key"]

        # Get the service template by ID
        get_result = await client.call_tool("get_itsi_service_template", {"template_id": template_id})
        assert "Error getting ITSI service template" not in get_result.data
        
        # Delete the test service template
        delete_result = await client.call_tool("delete_itsi_service_template", {"template_id": template_id})
        assert "Error deleting ITSI service template" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_deep_dives():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_deep_dives")
        assert "Error listing ITSI deep dives" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_deep_dive():
    async with Client(mcp_server) as client:
        # Create a test deep dive
        create_result = await client.call_tool("create_itsi_deep_dive", {"title": "Test Deep Dive", "description": "A test deep dive"})
        assert "Error creating ITSI deep dive" not in create_result.data
        deep_dive_data = eval(create_result.data)
        deep_dive_id = deep_dive_data["_key"]

        # Get the deep dive by ID
        get_result = await client.call_tool("get_itsi_deep_dive", {"deep_dive_id": deep_dive_id})
        assert "Error getting ITSI deep dive" not in get_result.data
        
        # Delete the test deep dive
        delete_result = await client.call_tool("delete_itsi_deep_dive", {"deep_dive_id": deep_dive_id})
        assert "Error deleting ITSI deep dive" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_glass_tables():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_glass_tables")
        assert "Error listing ITSI glass tables" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_glass_table():
    async with Client(mcp_server) as client:
        # Create a test glass table
        create_result = await client.call_tool("create_itsi_glass_table", {"title": "Test Glass Table", "description": "A test glass table"})
        assert "Error creating ITSI glass table" not in create_result.data
        table_data = eval(create_result.data)
        table_id = table_data["_key"]

        # Get the glass table by ID
        get_result = await client.call_tool("get_itsi_glass_table", {"table_id": table_id})
        assert "Error getting ITSI glass table" not in get_result.data
        
        # Delete the test glass table
        delete_result = await client.call_tool("delete_itsi_glass_table", {"table_id": table_id})
        assert "Error deleting ITSI glass table" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_home_views():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_home_views")
        assert "Error listing ITSI home views" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_home_view():
    async with Client(mcp_server) as client:
        # Create a test home view
        create_result = await client.call_tool("create_itsi_home_view", {"title": "Test Home View", "description": "A test home view"})
        assert "Error creating ITSI home view" not in create_result.data
        view_data = eval(create_result.data)
        view_id = view_data["_key"]

        # Get the home view by ID
        get_result = await client.call_tool("get_itsi_home_view", {"view_id": view_id})
        assert "Error getting ITSI home view" not in get_result.data
        
        # Delete the test home view
        delete_result = await client.call_tool("delete_itsi_home_view", {"view_id": view_id})
        assert "Error deleting ITSI home view" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_kpi_templates():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_kpi_templates")
        assert "Error listing ITSI KPI templates" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_kpi_template():
    async with Client(mcp_server) as client:
        # Create a test kpi template
        create_result = await client.call_tool("create_itsi_kpi_template", {"title": "Test KPI Template", "description": "A test kpi template"})
        assert "Error creating ITSI KPI template" not in create_result.data
        template_data = eval(create_result.data)
        template_id = template_data["_key"]

        # Get the kpi template by ID
        get_result = await client.call_tool("get_itsi_kpi_template", {"template_id": template_id})
        assert "Error getting ITSI KPI template" not in get_result.data
        
        # Delete the test kpi template
        delete_result = await client.call_tool("delete_itsi_kpi_template", {"template_id": template_id})
        assert "Error deleting ITSI KPI template" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_kpi_threshold_templates():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_kpi_threshold_templates")
        assert "Error listing ITSI KPI threshold templates" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_kpi_threshold_template():
    async with Client(mcp_server) as client:
        # Create a test kpi threshold template
        create_result = await client.call_tool("create_itsi_kpi_threshold_template", {"title": "Test KPI Threshold Template", "description": "A test kpi threshold template"})
        assert "Error creating ITSI KPI threshold template" not in create_result.data
        template_data = eval(create_result.data)
        template_id = template_data["_key"]

        # Get the kpi threshold template by ID
        get_result = await client.call_tool("get_itsi_kpi_threshold_template", {"template_id": template_id})
        assert "Error getting ITSI KPI threshold template" not in get_result.data
        
        # Delete the test kpi threshold template
        delete_result = await client.call_tool("delete_itsi_kpi_threshold_template", {"template_id": template_id})
        assert "Error deleting ITSI KPI threshold template" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_kpi_base_searches():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_kpi_base_searches")
        assert "Error listing ITSI KPI base searches" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_kpi_base_search():
    async with Client(mcp_server) as client:
        # Create a test kpi base search
        create_result = await client.call_tool("create_itsi_kpi_base_search", {"title": "Test KPI Base Search", "description": "A test kpi base search"})
        assert "Error creating ITSI KPI base search" not in create_result.data
        search_data = eval(create_result.data)
        search_id = search_data["_key"]

        # Get the kpi base search by ID
        get_result = await client.call_tool("get_itsi_kpi_base_search", {"search_id": search_id})
        assert "Error getting ITSI KPI base search" not in get_result.data
        
        # Delete the test kpi base search
        delete_result = await client.call_tool("delete_itsi_kpi_base_search", {"search_id": search_id})
        assert "Error deleting ITSI KPI base search" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_notable_events():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_notable_events")
        assert "Error listing ITSI notable events" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_notable_event():
    async with Client(mcp_server) as client:
        # Create a test notable event
        create_result = await client.call_tool("create_itsi_notable_event", {"title": "Test Notable Event", "description": "A test notable event"})
        assert "Error creating ITSI notable event" not in create_result.data
        event_data = eval(create_result.data)
        event_id = event_data["_key"]

        # Get the notable event by ID
        get_result = await client.call_tool("get_itsi_notable_event", {"event_id": event_id})
        assert "Error getting ITSI notable event" not in get_result.data
        
        # Delete the test notable event
        delete_result = await client.call_tool("delete_itsi_notable_event", {"event_id": event_id})
        assert "Error deleting ITSI notable event" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_correlation_searches():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_correlation_searches")
        assert "Error listing ITSI correlation searches" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_correlation_search():
    async with Client(mcp_server) as client:
        # Create a test correlation search
        create_result = await client.call_tool("create_itsi_correlation_search", {"title": "Test Correlation Search", "description": "A test correlation search"})
        assert "Error creating ITSI correlation search" not in create_result.data
        search_data = eval(create_result.data)
        search_id = search_data["_key"]

        # Get the correlation search by ID
        get_result = await client.call_tool("get_itsi_correlation_search", {"search_id": search_id})
        assert "Error getting ITSI correlation search" not in get_result.data
        
        # Delete the test correlation search
        delete_result = await client.call_tool("delete_itsi_correlation_search", {"search_id": search_id})
        assert "Error deleting ITSI correlation search" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_maintenance_calendars():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_maintenance_calendars")
        assert "Error listing ITSI maintenance calendars" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_maintenance_calendar():
    async with Client(mcp_server) as client:
        # Create a test maintenance calendar
        create_result = await client.call_tool("create_itsi_maintenance_calendar", {"title": "Test Maintenance Calendar", "description": "A test maintenance calendar"})
        assert "Error creating ITSI maintenance calendar" not in create_result.data
        calendar_data = eval(create_result.data)
        calendar_id = calendar_data["_key"]

        # Get the maintenance calendar by ID
        get_result = await client.call_tool("get_itsi_maintenance_calendar", {"calendar_id": calendar_id})
        assert "Error getting ITSI maintenance calendar" not in get_result.data
        
        # Delete the test maintenance calendar
        delete_result = await client.call_tool("delete_itsi_maintenance_calendar", {"calendar_id": calendar_id})
        assert "Error deleting ITSI maintenance calendar" not in delete_result.data

@pytest.mark.asyncio
async def test_list_itsi_teams():
    async with Client(mcp_server) as client:
        result = await client.call_tool("list_itsi_teams")
        assert "Error listing ITSI teams" not in result.data

@pytest.mark.asyncio
async def test_get_itsi_team():
    async with Client(mcp_server) as client:
        # Create a test team
        create_result = await client.call_tool("create_itsi_team", {"title": "Test Team", "description": "A test team"})
        assert "Error creating ITSI team" not in create_result.data
        team_data = eval(create_result.data)
        team_id = team_data["_key"]

        # Get the team by ID
        get_result = await client.call_tool("get_itsi_team", {"team_id": team_id})
        assert "Error getting ITSI team" not in get_result.data
        
        # Delete the test team
        delete_result = await client.call_tool("delete_itsi_team", {"team_id": team_id})
        assert "Error deleting ITSI team" not in delete_result.data
