import asyncio
import logging
import socket
import sys
import traceback
from fastmcp import Client, FastMCP
import platform
import ssl

# Comprehensive Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_debug.log', mode='w')
    ]
)
logger = logging.getLogger('MCPDiagnostics')

def system_diagnostics():
    """Collect system and network diagnostics."""
    logger.info("System Diagnostics:")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Network Hostname: {socket.gethostname()}")

def check_port_open(host, port, timeout=5):
    """Advanced port availability check."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            logger.info(f"Port {port} is open and reachable.")
            return True
    except (socket.timeout, ConnectionRefusedError) as e:
        logger.error(f"Port {port} connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected port check error: {e}")
        return False

async def advanced_mcp_connection_test(host, port, path="/"):
    """Comprehensive MCP connection diagnostic."""
    connection_url = f"http://{host}:{port}{path}"
    logger.info(f"Attempting connection to: {connection_url}")
    logger.info(f"Using MCP endpoint path: {path}")

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            logger.info(f"Connection Attempt {attempt + 1}/{max_attempts}")
            
            # Enhanced connection with more detailed timeout
            async with Client(connection_url, timeout=20) as client:
                logger.info("Successfully established MCP client connection.")

                # Diagnostic tool calls with comprehensive error handling
                diagnostic_tools = [
                    "list_indexes", 
                    "get_server_info", 
                    "list_available_tools"
                ]

                for tool in diagnostic_tools:
                    try:
                        logger.info(f"Calling diagnostic tool: {tool}")
                        result = await client.call_tool(tool)
                        logger.info(f"{tool.replace('_', ' ').title()} Result: {result.data}")
                    except Exception as tool_error:
                        logger.error(f"Error calling {tool} tool: {tool_error}")
                        logger.error(traceback.format_exc())
                
                # If all tools succeed, break the retry loop
                break

        except Exception as connection_error:
            logger.error(f"Connection Attempt {attempt + 1} Failed")
            logger.error(f"Error Type: {type(connection_error)}")
            logger.error(f"Error Details: {connection_error}")
            
            # If this was the last attempt, log full traceback
            if attempt == max_attempts - 1:
                logger.error("Full Traceback:")
                logger.error(traceback.format_exc())
                raise
            
            # Wait before next attempt
            await asyncio.sleep(2)

async def main():
    host = "192.168.1.210"
    port = 8333
    # Expanded list of potential endpoint paths
    paths = [
        "/",
        "/mcp",
        "/api/mcp",
        "/services/mcp",
        "/api/v1/mcp",
        "/v1/mcp",
        "/jsonrpc",
        "/rpc",
        "/api"
    ]

    # System and Network Diagnostics
    system_diagnostics()

    # Port Availability Check
    if not check_port_open(host, port):
        logger.critical(f"Cannot proceed: Port {port} is not accessible.")
        return

    # Test multiple potential endpoint paths
    connection_success = False
    for path in paths:
        try:
            logger.info(f"\n{'='*40}")
            logger.info(f"Testing endpoint path: '{path}'")
            await advanced_mcp_connection_test(host, port, path)
            connection_success = True
            logger.info(f"Successfully connected using path: '{path}'")
            break  # Stop after first successful connection
        except Exception as e:
            logger.error(f"Endpoint path '{path}' failed: {str(e)}")
            logger.error("Possible causes:")
            logger.error("- Server not configured for this endpoint")
            logger.error("- Protocol version mismatch")
            logger.error("- Docker container port mapping issue")
    
    if not connection_success:
        logger.error("All endpoint paths failed. Possible solutions:")
        logger.error("1. Check server configuration and logs")
        logger.error("2. Verify Docker port mapping and network settings")
        logger.error("3. Confirm MCP protocol version compatibility")
    
    logger.info("Completed all endpoint path tests")

if __name__ == "__main__":
    asyncio.run(main())
