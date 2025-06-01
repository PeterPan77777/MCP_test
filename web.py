"""
Web runner for Railway deployment
Starts the MCP server with HTTP transport
"""
import os
import uvicorn
from server import mcp

# Get the ASGI app from FastMCP
# This supports both streamable-http and SSE
app = mcp.http_app()

if __name__ == "__main__":
    # Get port from environment or use 8080
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Simple MCP Server on port {port}")
    print(f"📍 Endpoints:")
    print(f"   - Streamable HTTP: http://localhost:{port}/mcp")
    print(f"   - Health check: http://localhost:{port}/health")
    print(f"   - SSE (legacy): http://localhost:{port}/sse")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 