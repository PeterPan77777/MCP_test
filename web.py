# web.py  — kleinste funktionierende Version
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from server import mcp, init_engineering_tools
import json
from datetime import datetime

# Request Logging Middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log Request Details
        print(f"\n{'='*60}")
        print(f"📥 INCOMING REQUEST - {datetime.now().isoformat()}")
        print(f"{'='*60}")
        print(f"Method: {request.method}")
        print(f"Path: {request.url.path}")
        print(f"Headers: {dict(request.headers)}")
        
        # Log Request Body für POST/PUT
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            if body:
                try:
                    # Versuche als JSON zu parsen für schönere Ausgabe
                    json_body = json.loads(body)
                    print(f"Body (JSON):\n{json.dumps(json_body, indent=2)}")
                except:
                    # Falls kein JSON, als Text ausgeben
                    print(f"Body (Raw): {body.decode('utf-8', errors='ignore')}")
            
            # Request neu erstellen, da body consumed wurde
            from starlette.requests import Request
            request = Request(request.scope, receive=lambda: {"type": "http.request", "body": body})
        
        # Process Request
        response = await call_next(request)
        
        # Log Response Status
        print(f"\n📤 RESPONSE")
        print(f"Status: {response.status_code}")
        print(f"{'='*60}\n")
        
        return response

# 1️⃣  Sub-Apps: internes Prefix entfernen (path="/")
http_app = mcp.http_app(path="/")                        # registriert "/"
sse_app  = mcp.http_app(transport="sse", path="/")       # registriert "/"

# 2️⃣  Redirect-Schalter im Kinder-Router
http_app.router.redirect_slashes = True
sse_app.router.redirect_slashes  = True

# 3️⃣  Health-Route
async def health(_): 
    print(f"🏥 Health check called at {datetime.now().isoformat()}")
    return PlainTextResponse("OK")

# 4️⃣  Haupt-App mit erweitertem Lifespan für Engineering-Tools
async def lifespan(app):
    # Startup: Engineering-Tools initialisieren
    print(f"\n🚀 Starting MCP Engineering Server...")
    await init_engineering_tools()
    print(f"✅ Server ready for connections\n")
    
    # Original lifespan durchführen
    async with http_app.lifespan(app):
        yield

# Middleware für Logging
middleware = [
    Middleware(RequestLoggingMiddleware)
]

app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=lifespan,
    middleware=middleware
)
app.router.redirect_slashes = False                     # root-Router

# 5️⃣  *Ein* Mount je Transport – mit korrektem Präfix
app.mount("/mcp", http_app)                             # ergibt   /mcp
app.mount("/sse", sse_app)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"\n🌐 Starting server on port {port}")
    print(f"📍 Endpoints:")
    print(f"   - Health: http://0.0.0.0:{port}/health")
    print(f"   - MCP: http://0.0.0.0:{port}/mcp")
    print(f"   - SSE: http://0.0.0.0:{port}/sse")
    print(f"\n📋 Request logging enabled - all requests will be logged\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
