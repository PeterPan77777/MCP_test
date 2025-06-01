"""
Web runner for Railway deployment
Starts the MCP server with HTTP transport
"""
import os
import uvicorn
from server import mcp
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.responses import JSONResponse

# Create the main app
app = Starlette()

# Get MCP apps without path parameter (mounting will handle the path)
http_app = mcp.http_app()
sse_app = mcp.http_app(transport="sse")

# Mount the apps at specific paths
app.mount("/mcp", http_app)
app.mount("/sse", sse_app)

# Add root endpoint
@app.route("/")
async def root(request):
    return JSONResponse({
        "service": "Simple MCP Server",
        "version": "1.0",
        "endpoints": {
            "mcp": "/mcp",
            "sse": "/sse",
            "health": "/health"
        }
    })

# Add health endpoint at root level
@app.route("/health")
async def health(request):
    return JSONResponse({"status": "healthy", "service": "simple-mcp-server"})

if __name__ == "__main__":
    # Get port from environment or use 8080
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Simple MCP Server on port {port}")
    print(f"📍 Endpoints:")
    print(f"   - Root: http://localhost:{port}/")
    print(f"   - Streamable HTTP: http://localhost:{port}/mcp")
    print(f"   - SSE: http://localhost:{port}/sse")
    print(f"   - Health check: http://localhost:{port}/health")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 