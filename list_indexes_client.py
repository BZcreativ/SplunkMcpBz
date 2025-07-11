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

    print(f"Network Diagnostics for {host}:{port}")
    
    # Check port availability
    print("\nChecking port availability...")
    if not check_port_open(host, port):
        print(f"ERROR: Port {port} is not open!")
        return

    print("\nAttempting FastMCP connection...")
    try:
        async with Client(f"http://{host}:{port}/api/v1/mcp", timeout=30) as client:
            print("Connected to FastMCP server successfully!")
            
            print("Calling list_indexes tool...")
            result = await client.call_tool("list_indexes")
            print(f"Result: {result.data}")
            
            print("Calling get_server_info tool...")
            result2 = await client.call_tool("get_server_info")
            print(f"Server Info: {result2.data}")
            
    except Exception as e:
        print(f"Detailed FastMCP Connection Error:")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        print("Full Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
