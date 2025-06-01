# web.py  — kleinste funktionierende Version
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

# Streamable HTTP  ➜  internes /mcp  ➜  KEIN weiteres Prefix
http_app = mcp.http_app(path="")              # <– wichtig!
http_app.router.redirect_slashes = False      # vermeidet 307

# SSE  ➜  internes /sse  ➜  darf NICHT erneut gemountet werden
sse_app  = mcp.http_app(transport="sse")      # path="" nicht nötig
# (Prefix-Bug: Mount-Pfad wird verworfen; intern bleibt /sse)

# 2) Health-Endpoint
async def health(_):
    return PlainTextResponse("OK")

# 3) Starlette-Hülle
app = Starlette(lifespan=http_app.lifespan)
app.add_route("/health", health, methods=["GET"])

# ▸ Nur EIN Mount-Prefix pro Sub-App
app.mount("/mcp", http_app)   # ergibt genau  /mcp
app.mount("/",   sse_app)     # behält       /sse  + /sse/messages

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
