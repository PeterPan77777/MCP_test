import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

# 1️⃣ Streamable-HTTP-App – mit Default-Prefix `/mcp`
http_app = mcp.http_app()                   # NICHT path="/"
# 2️⃣ SSE-App – Default-Prefix `/sse`
sse_app  = mcp.http_app(transport="sse")    # ebenfalls Default-Prefix

# 2️⃣ Health-Endpoint
async def health(_): 
    return PlainTextResponse("OK")

# 3️⃣ Haupt-Starlette-App
app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=http_app.lifespan              # Session-Manager aktiv
)

# 4️⃣ Mounts (keine Doppel-Prefixe mehr)
app.mount("/", http_app)                    # ergibt …/mcp
app.mount("/", sse_app)                     # ergibt …/sse

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080))) 