import asyncio
import traceback
import socket
from fastmcp import Client
import sys

async def main():
    host = "192.168.1.210"
    port = 8333

    print(f"Python Version: {sys.version}")
    print(f"FastMCP Version: {Client.__module__}")
    
    try:
        print("\nAttempting FastMCP connection...")
        async with Client(f"http://{host}:{port}/", timeout=30) as client:
            print("Connected to FastMCP server successfully!")
            
            print("Available tools:")
            tools = await client.list_tools()
            print(tools)
            
    except Exception as e:
        print(f"Detailed FastMCP Connection Error:")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        print("Full Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
