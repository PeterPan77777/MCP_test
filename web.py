"""
Web runner for Railway deployment - Fixed with proper lifespan
"""
import os
import uvicorn
from server import mcp
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse, PlainTextResponse

# Get the MCP app (Streamable HTTP default)
mcp_app = mcp.http_app()

# Health check handler
async def health_check(request):
    return PlainTextResponse("OK")

# Meta info handler
async def meta(request):
    return JSONResponse({
        "service": "Simple MCP Server",
        "version": "1.0", 
        "endpoints": {
            "mcp_post": "POST /mcp - Start MCP session",
            "mcp_get": "GET /mcp - SSE stream",
            "health": "GET /health",
            "delete": "DELETE /mcp - End session"
        },
        "note": "FIXED: Added lifespan=mcp_app.lifespan",
        "usage": {
            "test_post": "curl -X POST -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"id\":1}' /mcp",
            "test_sse": "curl /mcp"
        }
    })

# Create main app with CRITICAL lifespan parameter!
app = Starlette(
    routes=[
        Mount("/", app=mcp_app),  # MCP app at root - provides /mcp endpoint
        Route("/health", health_check, methods=["GET"]),  # Health check
        Route("/meta", meta, methods=["GET"]),  # Meta info
    ],
    lifespan=mcp_app.lifespan  # ⚠️ OHNE DIES: 404 auf alle /mcp Routen!
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting MCP Server with proper lifespan on port {port}")
    print(f"📍 Endpoints:")
    print(f"   - POST /mcp → MCP JSON-RPC")
    print(f"   - GET /mcp → SSE Stream") 
    print(f"   - DELETE /mcp → End session")
    print(f"   - GET /health → Health check")
    print(f"   - GET /meta → This info")
    print(f"🔧 CRITICAL: lifespan=mcp_app.lifespan added!")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 