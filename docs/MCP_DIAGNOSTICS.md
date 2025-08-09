# MCP Connection Diagnostics

## Overview
This diagnostic script helps troubleshoot connection issues with a FastMCP server.

## Prerequisites
- Python 3.8+
- fastmcp library installed
- Network access to the MCP server

## Installation
```bash
pip install fastmcp
```

## Usage
```bash
python comprehensive_mcp_debug.py
```

## Diagnostic Outputs
- Console logs showing connection progress
- `mcp_debug.log` with detailed diagnostic information

## Troubleshooting Checklist
1. Verify server IP and port
2. Check network connectivity
3. Validate FastMCP version compatibility
4. Review server configuration

## Common Issues
- Firewall blocking connection
- Incorrect server URL
- Version mismatches
- Network routing problems

## Recommended Actions
1. Review `mcp_debug.log`
2. Check server logs
3. Verify network configuration
4. Confirm FastMCP version (current: 2.10.2)

## Diagnostic Features
- System information collection
- Network port accessibility check
- Advanced connection testing with retry mechanism
- Multiple diagnostic tool calls
- Comprehensive error logging
- Detailed connection attempt tracking

## Retry Mechanism
- Maximum of 3 connection attempts
- 2-second delay between retry attempts
- Detailed logging for each connection attempt
- Comprehensive error tracking

## Diagnostic Tools Tested
- list_indexes
- get_server_info
- list_available_tools

## Troubleshooting Tips
- Ensure server is running
- Check firewall settings
- Verify network routing
- Confirm server URL and port
