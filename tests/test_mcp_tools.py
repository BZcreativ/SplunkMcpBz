import pytest
import os
from fastmcp import Client
from src.splunk_mcp.main import mcp

# Skip tests if no Splunk credentials are available
splunk_credentials_available = bool(os.getenv("SPLUNK_TOKEN"))

@pytest.mark.skipif(not splunk_credentials_available, reason="Splunk credentials not available")
@pytest.mark.asyncio
async def test_mcp_health_check():
    """Test MCP health check"""
    async with Client(mcp) as client:
        result = await client.call_tool("mcp_health_check")
        assert result is not None

@pytest.mark.skipif(not splunk_credentials_available, reason="Splunk credentials not available")
@pytest.mark.asyncio
async def test_list_indexes():
    """Test list_indexes tool"""
    async with Client(mcp) as client:
        result = await client.call_tool("list_indexes")
        assert result is not None

@pytest.mark.skipif(not splunk_credentials_available, reason="Splunk credentials not available")
@pytest.mark.asyncio
async def test_get_itsi_services():
    """Test get_itsi_services tool"""
    async with Client(mcp) as client:
        result = await client.call_tool("get_itsi_services")
        assert result is not None