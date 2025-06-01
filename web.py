"""
Web runner for Railway deployment
Direct MCP server without complex routing
"""
import os
import uvicorn
from server import mcp
from starlette.responses import JSONResponse

# Get the MCP HTTP app directly
# This already handles /mcp routes internally
app = mcp.http_app()

# Add custom routes for root and health
@app.route("/", methods=["GET"])
async def root(request):
    return JSONResponse({
        "service": "Simple MCP Server",
        "version": "1.0",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        }
    })

@app.route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "healthy", "service": "simple-mcp-server"})

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