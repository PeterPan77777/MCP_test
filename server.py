"""
Simple MCP Server - Minimal example with SSE and streamable-http support
"""
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

# Create MCP server instance
mcp = FastMCP(
    name="simple-mcp-server",
    instructions="A minimal MCP server example"
)

# Add custom routes
@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """Root endpoint with service info."""
    return JSONResponse({
        "service": "Simple MCP Server",
        "version": "1.0",
        "endpoints": {
            "mcp": "/mcp",
            "sse": "/sse",
            "health": "/health"
        }
    })

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("OK")

# Tool 1: Simple echo tool
@mcp.tool()
def echo(message: str) -> str:
    """Echo back the message."""
    return f"Echo: {message}"

# Tool 2: Calculator
@mcp.tool()
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Examples:
    - "2 + 2"
    - "10 * 5"
    - "100 / 4"
    """
    try:
        # Only allow safe math operations
        allowed_chars = "0123456789+-*/. ()"
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Error: Only basic math operations are allowed"
    except Exception as e:
        return f"Error: {str(e)}"

# Tool 3: Get server info
@mcp.tool()
def server_info() -> str:
    """Get information about this MCP server."""
    return """
Simple MCP Server v1.0
======================
Available tools:
- echo: Echo back a message
- calculate: Evaluate math expressions
- server_info: This information

Supports:
- SSE transport
- Streamable HTTP transport
"""

# Main entry point
if __name__ == "__main__":
    # Run with default transport (stdio)
    # For Railway, we'll use a separate runner file
    mcp.run() 