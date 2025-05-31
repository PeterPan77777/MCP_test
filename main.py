#!/usr/bin/env python3
"""
Entry point für DigitalOcean Deployment
Nutzt FastMCP 2.5.2 mit ASGI App
"""
import os
from app.main import mcp
import uvicorn

if __name__ == "__main__":
    # Port aus Environment oder Standard 8080
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Context7 MCP Server on port {port}")
    print(f"📦 FastMCP Version: 2.5.2")
    print(f"🌐 Endpoints:")
    print(f"   - Health: http://0.0.0.0:{port}/health")
    print(f"   - SSE: http://0.0.0.0:{port}/sse")
    print(f"   - MCP: http://0.0.0.0:{port}/mcp")
    print(f"   - Info: http://0.0.0.0:{port}/")
    
    # Hole die ASGI App von FastMCP
    app = mcp.http_app()
    
    # Starte mit uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    ) 