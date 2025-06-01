import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

# 1️⃣ Sub-Apps erzeugen
http_app = mcp.http_app(path="/")                        # Streamable HTTP
sse_app  = mcp.http_app(transport="sse", path="/")       # SSE Transport

# 2️⃣ Health-Endpoint
async def health(_): 
    return PlainTextResponse("OK")

# 3️⃣ Haupt-App
app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=http_app.lifespan                           # wichtig!
)

# 4️⃣ Mount – Endpunkte festlegen
app.mount("/mcp", http_app)                              # POST/GET/DELETE
app.mount("/sse", sse_app)                               # GET /sse (SSE)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080))) 