# web.py  – 100 % kompatibel zu Inspector, /mcp & /sse
import os, uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import PlainTextResponse
from server import mcp                    # deine Tools

# ①  Streamable HTTP –  KEIN path-Parameter → behält /mcp
# web.py  (nur die relevanten Zeilen geändert)

http_app = mcp.http_app()                           # behält internes /mcp
sse_app  = mcp.http_app(transport="sse", path="/")  # internes Prefix entfernen!

app = Starlette(
    routes=[Route("/health", health, methods=["GET"])],
    lifespan=http_app.lifespan
)

app.mount("/",     http_app)   # ergibt   /mcp
app.mount("/sse",  sse_app)    # ergibt   /sse   (nicht /sse/sse)


async def health(_):                      # Health-Probe für Railway
    return PlainTextResponse("OK")

app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),   # immer zuerst!
        Mount("/", http_app),                        # enthält /mcp …
        Mount("/sse", sse_app),                      # … und /sse getrennt
    ],
    lifespan=http_app.lifespan                       # wichtig für Routen-Init
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
