from typing import Dict, Any
from .main import get_splunk_service, SplunkQueryError

def execute_splunk_search(
    query: str,
    earliest_time: str = "-24h",
    latest_time: str = "now",
    output_mode: str = "json"
) -> Dict[str, Any]:
    """Core Splunk search logic that can be tested independently"""
    try:
        service = get_splunk_service()
        kwargs = {
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "output_mode": output_mode
        }
        search_results = service.jobs.oneshot(query, **kwargs)
        return {
            "results": list(search_results),
            "metadata": {
                "scan_count": search_results["scanCount"],
                "result_count": search_results["resultCount"]
            }
        }
    except Exception as e:
        raise SplunkQueryError(f"Search failed: {str(e)}") from e
