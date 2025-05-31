"""
DigitalOcean Python Environment Entry Point
"""
import os
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Port aus Environment oder Standard 8080
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting Context7 MCP Server on port {port}")
    print(f"🌐 Health Check: http://0.0.0.0:{port}/health")
    print(f"📡 SSE Endpoint: http://0.0.0.0:{port}/sse")
    print(f"🔗 MCP Endpoint: http://0.0.0.0:{port}/mcp")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        access_log=True
    ) 