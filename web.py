# web.py  – funktioniert mit Streamable HTTP unter /mcp und SSE unter /sse
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp                     # deine Tools

# 1)  Sub-Apps OHNE internes Präfix  →  path=""  (nicht "/")
http_app = mcp.http_app(path="")                      # /mcp
sse_app  = mcp.http_app(transport="sse", path="")     # /sse

# 2)  Health-Route
async def health(_): 
    return PlainTextResponse("OK")

# 3)  Haupt-App
app = Starlette(lifespan=http_app.lifespan)
app.router.redirect_slashes = False                  # 307-Redirects aus
app.add_route("/health", health, methods=["GET"])    # Health zuerst
app.mount("/mcp", http_app)                          # Streamable HTTP
app.mount("/sse", sse_app)                           # SSE

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
