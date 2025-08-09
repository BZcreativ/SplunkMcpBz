import pytest
from unittest.mock import patch, MagicMock
from src.splunk_mcp.search_helper import execute_splunk_search
from src.splunk_mcp.main import SplunkQueryError

def test_successful_search():
    with patch('src.splunk_mcp.search_helper.get_splunk_service') as mock_service:
        # Create mock results that can be both iterated and accessed as dict
        class MockResults:
            def __init__(self, data):
                self.data = data
                self.scanCount = 2
                self.resultCount = 2
            
            def __iter__(self):
                return iter(self.data)
            
            def __getitem__(self, key):
                return getattr(self, key)

        mock_results = MockResults([
            {"_raw": "test event 1", "_time": "2025-07-13T12:00:00"},
            {"_raw": "test event 2", "_time": "2025-07-13T12:01:00"}
        ])

        # Setup mock service chain
        mock_service.return_value.jobs.oneshot.return_value = mock_results

        result = execute_splunk_search("test query")
        print(f"Mock service calls: {mock_service.mock_calls}")  # Debug
        print(f"Test results: {result}")  # Debug
        assert len(result["results"]) == 2
        assert result["metadata"]["scan_count"] == 2

def test_failed_search():
    with patch('src.splunk_mcp.search_helper.get_splunk_service') as mock_service:
        mock_service.return_value.jobs.oneshot.side_effect = Exception("Search failed")
        
        with pytest.raises(SplunkQueryError):
            execute_splunk_search("invalid query")

def test_time_parameters():
    with patch('src.splunk_mcp.search_helper.get_splunk_service') as mock_service:
        mock_job = MagicMock()
        mock_job.oneshot.return_value = []
        mock_service.return_value.jobs.oneshot.return_value = mock_job

        execute_splunk_search(
            "test",
            earliest_time="-1h",
            latest_time="now"
        )
        mock_service.return_value.jobs.oneshot.assert_called_with(
            "test", earliest_time="-1h", latest_time="now", output_mode="json"
        )
