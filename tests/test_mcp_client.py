import pytest
from fastmcp import Client
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_mcp_client_connection():
    mcp_config = {
      "name": "SplunkMCP",
      "protocol": "http",
      "url": "http://192.168.1.210:8333",
      "roots": [
        {
          "uri": "file:///path/to/your/SplunkMCP",
          "name": "SplunkMCP"
        }
      ]
    }

    mock_result = AsyncMock()
    mock_result.data = "test"

    with patch("fastmcp.Client.call_tool", return_value=mock_result) as mock_call_tool:
        client = Client(mcp_config["url"])
        result = await client.call_tool("search_splunk", {"query": "search index=_internal | head 1"})
        assert result.data == "test"
        mock_call_tool.assert_called_once_with("search_splunk", {"query": "search index=_internal | head 1"})
