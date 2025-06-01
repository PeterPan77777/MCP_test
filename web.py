# web.py  — kleinste funktionierende Version
import os, uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from server import mcp

# 1️⃣  Sub-Apps: internes Prefix entfernen (path="/")
http_app = mcp.http_app(path="/")                        # registriert "/"
sse_app  = mcp.http_app(transport="sse", path="/")       # registriert "/"

# 2️⃣  Redirect-Schalter im Kinder-Router
http_app.router.redirect_slashes = True
sse_app.router.redirect_slashes  = True

# 3️⃣  Health-Route
async def health(_): 
    return PlainTextResponse("OK")

# 4️⃣  Haupt-App
app = Starlette(routes=[Route("/health", health, methods=["GET"])],
                lifespan=http_app.lifespan)
app.router.redirect_slashes = False                     # root-Router

# 5️⃣  *Ein* Mount je Transport – mit korrektem Präfix
app.mount("/mcp", http_app)                             # ergibt   /mcp
app.mount("/sse", sse_app)
app.mount("/mcp/", http_app)                             # ergibt   /mcp
app.mount("/sse/", sse_app)                              # ergibt   /sse

# 🔍 DEBUG: Routen unmittelbar nach dem Mount ausgeben
print("=== DEBUG: Registrierte Routen ===")
for r in app.routes:
    print(f"▶ PATH: {getattr(r, 'path', '?')},  NAME: {r.name}")

# 🔍 DEBUG: Redirect-Einstellungen loggen
print("=== DEBUG: Redirect-Einstellungen ===")
print("Root redirect_slashes:", app.router.redirect_slashes)
print("HTTP redirect_slashes:", http_app.router.redirect_slashes)
print("SSE  redirect_slashes:", sse_app.router.redirect_slashes)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.getenv("PORT", 8080)))
