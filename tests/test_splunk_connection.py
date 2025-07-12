import pytest
from splunk_mcp.splunk_connector import SplunkConnector

def test_splunk_connection():
    connector = SplunkConnector()
    service = connector.connect()
    assert service is not None
    apps = service.apps
    assert len(apps) > 0
