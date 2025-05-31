#!/usr/bin/env python3
"""
Entry point für DigitalOcean Deployment
Nutzt FastMCP 2.5.2 ASGI App direkt mit uvicorn
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    try:
        # Importiere die ASGI App
        from app.main import mcp
        
        # Port aus Environment oder Standard 8080
        port = int(os.environ.get("PORT", 8080))
        
        print(f"🚀 Starting Context7 MCP Server")
        print(f"📦 FastMCP Version: 2.5.2")
        print(f"🌐 Port: {port}")
        print(f"📍 Endpoints:")
        print(f"   - Health: http://0.0.0.0:{port}/health")
        print(f"   - SSE: http://0.0.0.0:{port}/sse")
        print(f"   - MCP: http://0.0.0.0:{port}/mcp")
        print(f"   - Info: http://0.0.0.0:{port}/")
        
        # Hole die ASGI App von FastMCP
        app = mcp.http_app()
        
        # Starte direkt mit uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            # Wichtig für DigitalOcean
            workers=1,
            loop="asyncio"
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print(f"Python Version: {sys.version}")
        import traceback
        traceback.print_exc()
        
        # Fallback: Versuche die alte run() Methode
        print("\n🔄 Trying fallback method...")
        try:
            from app.main import mcp
            # Starte direkt ohne transport Parameter
            mcp.run()
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            sys.exit(1) 