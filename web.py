import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

mcp_app = mcp.http_app(path="/")          # MCP direkt auf /
PORT = int(os.getenv("PORT", 8080))

async def health(_):
    return PlainTextResponse("OK")

app = Starlette(
    routes=[("/health", health, ["GET"])],
    lifespan=mcp_app.lifespan,
    redirect_slashes=False                 # keine 307-Redirects
)
app.mount("/", mcp_app)                    # Basispfad → MCP

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info") 