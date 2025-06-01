# web.py  –  /mcp  (HTTP)  &  /sse  (SSE)  ohne nachgestelltes '/'
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

# 1️⃣  Sub-Apps OHNE Slash-Präfix
http_app = mcp.http_app(path="")                   # ergibt /mcp
sse_app  = mcp.http_app(transport="sse", path="")  # ergibt /sse

http_app.router.redirect_slashes = False           # keine 307-Redirects
sse_app.router.redirect_slashes  = False

async def health(_): return PlainTextResponse("OK")

app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=http_app.lifespan
)
app.router.redirect_slashes = False

app.mount("/mcp", http_app)                        # /mcp
app.mount("/sse", sse_app)                         # /sse

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
