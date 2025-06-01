# web.py  – funktioniert mit Streamable HTTP unter /mcp und SSE unter /sse
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Router
from server import mcp        # deine Tools

PORT = int(os.getenv("PORT", 8080))

# 1) Sub-Apps OHNE internes Prefix
http_app = mcp.http_app(path="/")                 # Streamable-HTTP
sse_app  = mcp.http_app(transport="sse", path="/")# SSE

# 2) Health-Route
async def health(_): 
    return PlainTextResponse("OK")

# 3) Eigenen Router anlegen, Redirects abschalten
router = Router(redirect_slashes=False)
router.mount("/mcp", http_app)                    # /mcp
router.mount("/sse", sse_app)                     # /sse

# 4) Haupt-App: Health zuerst, dann Mount aller Sub-Routen
app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        router                                    # alle /mcp & /sse Endpunkte
    ],
    lifespan=http_app.lifespan
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
