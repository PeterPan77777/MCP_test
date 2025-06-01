import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from server import mcp

mcp_app = mcp.http_app()              # behält internes /mcp
PORT = int(os.getenv("PORT", 8080))

async def health(_): 
    return PlainTextResponse("OK")

app = Starlette(
    routes=[
        # Health-Check zuerst, damit Railway ihn findet
        Route("/health", health, methods=["GET"]),
    ],
    lifespan=mcp_app.lifespan          # ⚠️ wichtig
)
app.mount("/", mcp_app)                # /mcp liegt jetzt top-level

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info") 