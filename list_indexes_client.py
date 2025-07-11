import asyncio
import traceback
import socket
from fastmcp import Client

def check_port_open(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Port check error: {e}")
        return False

async def main():
    host = "192.168.1.210"
    port = 8333

    print(f"Checking if port {port} is open on {host}...")
    if not check_port_open(host, port):
        print(f"ERROR: Port {port} is not open!")
        return

    try:
        print("Attempting to connect to server...")
        async with Client(f"http://{host}:{port}/", timeout=15, verify_ssl=False) as client:
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
