"""
Web runner for Railway deployment
Direct MCP server with HTTP transport
"""
import os
import uvicorn
from server import mcp

# Get the MCP HTTP app directly
# This already handles /mcp routes and our custom routes internally
app = mcp.http_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Simple MCP Server on port {port}")
    print(f"📍 Endpoints:")
    print(f"   - Root: http://localhost:{port}/")
    print(f"   - MCP: http://localhost:{port}/mcp")
    print(f"   - Health: http://localhost:{port}/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 