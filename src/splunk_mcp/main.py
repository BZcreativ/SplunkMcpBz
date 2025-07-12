from fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("SplunkMCP")

@mcp.tool()
async def health_check() -> dict:
    return {"status": "ok"}

app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8334)
