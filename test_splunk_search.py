import unittest
from unittest.mock import patch, MagicMock
from src.splunk_mcp.main import mcp, SplunkQueryError
from fastmcp.server.lowlevel.server import ToolCallRequest

class TestSplunkSearch(unittest.TestCase):
    def setUp(self):
        self.tool = next(t for t in mcp.tools.values() if t.name == "splunk_search")

    @patch('src.splunk_mcp.main.get_splunk_service')
    async def test_successful_search(self, mock_service):
        # Setup mock
        mock_job = MagicMock()
        mock_job.oneshot.return_value = [
            {"_raw": "test event 1", "_time": "2025-07-13T12:00:00"},
            {"_raw": "test event 2", "_time": "2025-07-13T12:01:00"}
        ]
        mock_job.oneshot.__getitem__.side_effect = lambda k: {
            "scanCount": 2,
            "resultCount": 2
        }[k]
        mock_service.return_value.jobs.oneshot.return_value = mock_job

        # Test
        request = ToolCallRequest(
            tool_name="splunk_search",
            arguments={"query": "test query"}
        )
        result = await self.tool.execute(request)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["metadata"]["scan_count"], 2)

    @patch('src.splunk_mcp.main.get_splunk_service')
    async def test_failed_search(self, mock_service):
        mock_service.return_value.jobs.oneshot.side_effect = Exception("Search failed")
        
        request = ToolCallRequest(
            tool_name="splunk_search",
            arguments={"query": "invalid query"}
        )
        with self.assertRaises(SplunkQueryError):
            await self.tool.execute(request)

    @patch('src.splunk_mcp.main.get_splunk_service')
    async def test_time_parameters(self, mock_service):
        mock_job = MagicMock()
        mock_job.oneshot.return_value = []
        mock_service.return_value.jobs.oneshot.return_value = mock_job

        request = ToolCallRequest(
            tool_name="splunk_search",
            arguments={
                "query": "test",
                "earliest_time": "-1h",
                "latest_time": "now"
            }
        )
        await self.tool.execute(request)
        mock_service.return_value.jobs.oneshot.assert_called_with(
            "test", earliest_time="-1h", latest_time="now", output_mode="json"
        )

if __name__ == "__main__":
    unittest.main()
