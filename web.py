# web.py  — kleinste funktionierende Version
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

# ① FastMCP-Sub-Apps OHNE path-Hack
http_app = mcp.http_app()                      # ➜ /mcp (+ /mcp/{id})
sse_app  = mcp.http_app(transport="sse")       # ➜ /sse (+ /sse/messages)

# ② Trailing-Slash-Redirects ausschalten – jeweils im Sub-Router
http_app.router.redirect_slashes = False       # verhindert 307 /mcp ➜ /mcp/
sse_app.router.redirect_slashes  = False       # nur der Vollständigkeit halber

# ③ Health-Endpoint
async def health(_): 
    return PlainTextResponse("OK")

# ④ Haupt-App – Health zuerst, dann beide Sub-Apps unter Root mounten
app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=http_app.lifespan                 # Session-Manager laden!
)
app.router.redirect_slashes = False           # auch im Root-Router
app.mount("/", http_app)                      # veröffentlicht /mcp
app.mount("/", sse_app)                       # veröffentlicht /sse

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
