import asyncio
from fastmcp import Client

async def main():
    try:
        async with Client("http://192.168.1.210:8333/") as client:
            print("Connected to FastMCP server successfully!")
            result = await client.call_tool("list_indexes")
            print(f"Result: {result.data}")
            
            # Test the second tool as well
            result2 = await client.call_tool("get_server_info")
            print(f"Server Info: {result2.data}")
            
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
