# web.py  — kleinste funktionierende Version
import os, uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from server import mcp

# 1) EIN FastMCP-ASGI App – enthält automatisch /mcp + /sse
mcp_app = mcp.http_app()                 # interne Pfade /mcp und /sse

# 2) Health-Endpoint
async def health(_):
    return PlainTextResponse("OK")

# 3) Starlette-Hülle
app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=mcp_app.lifespan            # wichtig!
)
app.router.redirect_slashes = False      # kein 307 auf /mcp
app.mount("/", mcp_app)                  # veröffentlicht /mcp & /sse

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
