"""
Direct MCP server runner for Railway
Uses MCP app directly as root application
"""
import os
import uvicorn
from server import mcp

# Get the MCP HTTP app directly
# This will handle /mcp at the root level
app = mcp.http_app()

if __name__ == "__main__":
    # Get port from environment or use 8080
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Direct MCP Server on port {port}")
    print(f"📍 MCP endpoint: http://localhost:{port}/mcp")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 