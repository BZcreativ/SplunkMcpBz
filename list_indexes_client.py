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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Server host:port")
    args = parser.parse_args()

    if args.host:
        if ":" in args.host:
            host, port = args.host.split(":")
            port = int(port)
        else:
            host = args.host
            port = 8334
    else:
        host = "localhost"
        port = 8334
    
    # Configure OAuth 2.1 with PKCE
    auth_config = {
        "oauth_version": "2.1",
        "pkce_required": True,
        "resource": f"http://{host}:{port}/mcp"
    }

    print(f"Network Diagnostics for {host}:{port}")
    print(f"Using OAuth 2.1 with PKCE for authentication")
    
    # Check port availability
    print("\nChecking port availability...")
    if not check_port_open(host, port):
        print(f"ERROR: Port {port} is not open!")
        print("Possible causes:")
        print("- Server not running")
        print("- Firewall blocking port")
        print("- Wrong IP address")
        print("- Server crashed")
        return

    print("\nServer connection details:")
    print(f"URL: http://{host}:{port}/mcp")
    print(f"Health endpoint: http://{host}:{port}/health")
    print(f"Timeout: 30 seconds")

    print("\nAttempting FastMCP connection...")
    print("Client configuration:")
    print(f"- URL: http://{host}:{port}/mcp")
    print(f"- Timeout: 30 seconds")
    print(f"- Async context manager")
    
    try:
        print("\nInitializing FastMCP client...")
        max_retries = 5  # Increased retry attempts
        retry_delay = 2  # Reduced delay between attempts
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} of {max_retries}")
                # Reduced timeout and added session keepalive
                # Try connecting to root path first
                async with Client(
                    f"http://localhost:{port}/mcp",
                    timeout=30
                ) as client:
                    print("Client initialized successfully")
                    print("Connected to FastMCP server successfully!")
                    
                    print("Calling list_indexes tool...")
                    result = await client.call_tool("list_indexes")
                    print(f"Result: {result.data}")
                    
                    print("Calling get_server_info tool...")
                    result2 = await client.call_tool("get_server_info")
                    print(f"Server Info: {result2.data}")
                    break  # Success - exit retry loop
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise  # Re-raise last error if all retries fail
            
    except Exception as e:
        print(f"Detailed FastMCP Connection Error:")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        print("Full Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
