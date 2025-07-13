import asyncio
from fastmcp import Client
import json

async def test_mcp_tools():
    host = "192.168.1.210"
    port = 8334
    
    tools_to_test = [
        ("mcp_health_check", {}),
        ("list_indexes", {}),
        ("get_server_info", {}),
        ("search_splunk", {"query": "* | head 5", "index": "main"})
    ]

    print(f"Testing MCP tools at {host}:{port}")
    
    try:
        async with Client(
            f"http://{host}:{port}/mcp",
            timeout=30
        ) as client:
            print("Connected to MCP server")
            
            for tool, params in tools_to_test:
                print(f"\nTesting tool: {tool}")
                print(f"Parameters: {json.dumps(params, indent=2)}")
                
                try:
                    result = await client.call_tool(tool, **params)
                    print("Success!")
                    print(f"Response: {json.dumps(result.data, indent=2)}")
                except Exception as e:
                    print(f"Failed to call {tool}: {str(e)}")

    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
