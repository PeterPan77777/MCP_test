"""
Web runner for Railway deployment - Fixed routing priority
"""
import os
import uvicorn
from server import mcp
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse, PlainTextResponse

# Get the MCP app (path="" to avoid double /mcp/mcp)
mcp_app = mcp.http_app(path="")

# Health check handler
async def health_check(request):
    return PlainTextResponse("OK")

# Root handler
async def root(request):
    return JSONResponse({
        "service": "Simple MCP Server",
        "version": "1.0", 
        "endpoints": {
            "health": "GET /health",
            "mcp": "POST /mcp - MCP JSON-RPC",
            "mcp_sse": "GET /mcp - SSE stream",
            "delete": "DELETE /mcp - End session"
        },
        "status": "healthy",
        "note": "FIXED: Mount under /mcp to avoid route priority issues"
    })

# Create main app with correct route priority!
app = Starlette(
    routes=[
        Route("/health", health_check, methods=["GET"]),  # Health check FIRST
        Route("/", root, methods=["GET"]),                # Root info
        Mount("/mcp", app=mcp_app),                       # MCP app unter /mcp (nicht /)
    ],
    lifespan=mcp_app.lifespan  # Critical for session manager
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting MCP Server on port {port}")
    print(f"📍 Endpoints:")
    print(f"   - GET / → Service info")
    print(f"   - GET /health → Health check (for Railway)")
    print(f"   - POST /mcp → MCP JSON-RPC")
    print(f"   - GET /mcp → SSE Stream") 
    print(f"   - DELETE /mcp → End session")
    print(f"🔧 FIXED: Mount under /mcp, not / (route priority)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 