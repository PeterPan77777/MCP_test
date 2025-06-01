# web.py  –  /mcp   und   /sse   ohne Slash  (Inspector kann beides)
import os, uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from server import mcp

# 1️⃣  Sub-Apps OHNE Slash-Prefix  (path="")
http_app = mcp.http_app(path="")                    # ->  /
sse_app  = mcp.http_app(transport="sse", path="")   # ->  /

# 2️⃣  307-Redirects ausschalten NUR für die Sub-Apps
http_app.router.redirect_slashes = False
sse_app.router.redirect_slashes  = False

# 3️⃣  Health-Check
async def health(_): return PlainTextResponse("OK")

# 4️⃣  Haupt-App
app = Starlette(routes=[Route("/health", health, methods=["GET"])],
                lifespan=http_app.lifespan)        # wichtig!
app.router.redirect_slashes = False               # Root ebenfalls

# 5️⃣  Mount mit exakt *einem* Präfix pro Transport
app.mount("/mcp", http_app)                       # finaler Pfad: /mcp
app.mount("/sse", sse_app)                        # finaler Pfad: /sse

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
