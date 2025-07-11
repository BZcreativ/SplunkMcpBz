import asyncio
import traceback
from fastmcp import Client

async def main():
    try:
        print("Attempting to connect to server...")
        async with Client("http://192.168.1.210:8333/", timeout=10, verify_ssl=False) as client:
            print("Connected to FastMCP server successfully!")
            
            print("Calling list_indexes tool...")
            result = await client.call_tool("list_indexes")
            print(f"Result: {result.data}")
            
            print("Calling get_server_info tool...")
            result2 = await client.call_tool("get_server_info")
            print(f"Server Info: {result2.data}")
            
    except Exception as e:
        print(f"Detailed Error:")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        print("Full Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
