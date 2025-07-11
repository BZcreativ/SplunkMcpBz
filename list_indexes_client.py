import asyncio
import traceback
import socket
import ssl
import urllib.request
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

def check_http_connectivity(host, port):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        url = f"http://{host}:{port}"
        print(f"Attempting HTTP request to {url}")
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            print(f"HTTP Response Code: {response.getcode()}")
            return True
    except Exception as e:
        print(f"HTTP connectivity check error: {e}")
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

    # Check HTTP connectivity
    print("\nChecking HTTP connectivity...")
    if not check_http_connectivity(host, port):
        print("ERROR: HTTP connectivity failed!")
        return

    try:
        print("\nAttempting FastMCP connection...")
        async with Client(f"http://{host}:{port}/", timeout=15, verify_ssl=False) as client:
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
