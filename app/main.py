"""
Context7 MCP Server - optimiert für DigitalOcean & n8n
Nutzt FastMCP 2.5.2 mit stateless HTTP für bessere Skalierbarkeit
"""
import uuid
import asyncio
import httpx
import json
from typing import Optional, Dict, Any
from fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import StreamingResponse, JSONResponse, PlainTextResponse
from sse_starlette import EventSourceResponse

# ---------- Context7 Client -------------
class Context7Client:
    """Client für Context7 API Zugriffe"""
    
    def __init__(self):
        self.base_url = "https://api.context7.dev"
        self.timeout = 30.0
    
    async def resolve_library_id(self, library_name: str) -> Dict[str, Any]:
        """Löst einen Library Namen zu einer Context7 Library ID auf"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/resolve-library-id",
                    json={"libraryName": library_name}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": f"Fehler beim Auflösen der Library ID: {str(e)}"}
    
    async def get_library_docs(self, library_id: str, topic: Optional[str] = None, tokens: int = 10000) -> Dict[str, Any]:
        """Holt Dokumentation für eine Library"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "context7CompatibleLibraryID": library_id,
                    "tokens": tokens
                }
                if topic:
                    payload["topic"] = topic
                
                response = await client.post(
                    f"{self.base_url}/get-library-docs",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": f"Fehler beim Abrufen der Dokumentation: {str(e)}"}

# Context7 Client Instanz
context7 = Context7Client()

# ---------- FastMCP Server -------------
# Stateless HTTP für bessere Skalierbarkeit auf DigitalOcean
mcp = FastMCP(
    name="Context7-DO-Server",
    instructions="Context7 MCP Server optimiert für DigitalOcean und n8n",
    stateless_http=True  # Kein Session-State, besser für Serverless
)

# ---------- Custom Routes -------------
@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """Root endpoint mit Service-Informationen"""
    return JSONResponse({
        "service": "Context7 MCP Server",
        "version": "2.0.0",
        "fastmcp": "2.5.2",
        "endpoints": {
            "health": "/health",
            "sse": "/sse (für n8n)",
            "mcp": "/mcp (Streamable HTTP)"
        },
        "features": {
            "stateless": True,
            "context7": True,
            "tools": ["echo", "hello", "resolve_library", "get_documentation", "search_and_document", "server_info"]
        },
        "status": "running"
    })

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health Check für DigitalOcean"""
    return PlainTextResponse("OK", status_code=200)

# --------- SSE für MCP Inspector & n8n (DigitalOcean Anti-Buffering) ----------
@mcp.custom_route("/sse", methods=["GET"])
async def sse_endpoint(request: Request) -> EventSourceResponse:
    """
    SSE Endpoint für MCP Inspector & n8n
    Optimiert für DigitalOcean mit Anti-Buffering Headers
    """
    
    async def event_stream():
        sid = uuid.uuid4().hex
        
        # 1️⃣ NUR Handshake-Frame (kein done-Frame!)
        # done-Frame bricht Inspector mit AbortError ab
        yield {
            "event": "endpoint",
            "data": f"/messages?sessionId={sid}"
        }
        
        # 2️⃣ Keep-alive alle 20s (DO-Proxy kappt nach ~55s)
        while True:
            await asyncio.sleep(20)  # Nicht 15s - 20s ist sicherer
            # Kommentar-Frame ist SSE-spec-konform und löst keine AbortErrors aus
            yield {"comment": "ping"}
    
    # DigitalOcean Anti-Buffering Headers (nach Best Practices)
    return EventSourceResponse(
        event_stream(),
        headers={
            # Kritische Anti-Buffering Headers
            "X-Accel-Buffering": "no",           # nginx/DO proxy buffering aus
            "Cache-Control": "no-cache, no-transform",  # Keine Kompression durch Proxies
            "Content-Encoding": "identity",      # Explizit keine gzip/br
            
            # SSE Standard Headers
            "Content-Type": "text/event-stream",
            "Connection": "keep-alive",
            
            # CORS für Inspector
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
            "Access-Control-Allow-Methods": "GET",
        },
    )

# ---------- MCP Tools -------------
@mcp.tool()
def echo(text: str) -> str:
    """Einfaches Echo-Tool zum Testen."""
    return f"Echo: {text}"

@mcp.tool()
def hello(name: str = "World") -> str:
    """Freundliche Begrüßung."""
    return f"👋 Hallo, {name}! Context7 MCP Server läuft auf FastMCP 2.5.2!"

@mcp.tool()
async def resolve_library(library_name: str) -> str:
    """
    Löst einen Library Namen zu einer Context7-kompatiblen Library ID auf.
    
    Args:
        library_name: Der Name der Library/des Packages (z.B. 'react', 'fastapi', 'numpy')
    
    Returns:
        Die Context7-kompatible Library ID oder eine Fehlermeldung
    """
    result = await context7.resolve_library_id(library_name)
    
    if "error" in result:
        return f"❌ {result['error']}"
    
    if "libraries" in result and result["libraries"]:
        library = result["libraries"][0]
        library_id = library.get("id", "Unbekannt")
        description = library.get("description", "Keine Beschreibung verfügbar")
        trust_score = library.get("trustScore", "Unbekannt")
        
        return f"""✅ Library gefunden:
📚 Library ID: {library_id}
📖 Beschreibung: {description}
⭐ Trust Score: {trust_score}

Verwende diese Library ID für get_documentation."""
    
    return f"❌ Keine Library gefunden für: {library_name}"

@mcp.tool()
async def get_documentation(library_id: str, topic: Optional[str] = None, max_tokens: int = 10000) -> str:
    """
    Holt aktuelle Dokumentation für eine Library von Context7.
    
    Args:
        library_id: Die Context7-kompatible Library ID (verwende resolve_library zuerst)
        topic: Optionales spezifisches Thema (z.B. 'hooks', 'routing', 'authentication')
        max_tokens: Maximale Anzahl Tokens der Dokumentation (Standard: 10000)
    
    Returns:
        Die Dokumentation oder eine Fehlermeldung
    """
    result = await context7.get_library_docs(library_id, topic, max_tokens)
    
    if "error" in result:
        return f"❌ {result['error']}"
    
    if "documentation" in result:
        docs = result["documentation"]
        
        response = f"""📚 Dokumentation für {library_id}
{'='*50}

"""
        
        if topic:
            response += f"🎯 Thema: {topic}\n\n"
        
        response += docs[:max_tokens]
        
        if len(docs) > max_tokens:
            response += f"\n\n📝 Hinweis: Dokumentation wurde auf {max_tokens} Zeichen begrenzt."
        
        return response
    
    return "❌ Keine Dokumentation verfügbar"

@mcp.tool()
async def search_and_document(library_name: str, topic: Optional[str] = None, max_tokens: int = 10000) -> str:
    """
    Kombiniert Library-Suche und Dokumentationsabruf in einem Schritt.
    
    Args:
        library_name: Der Name der Library/des Packages
        topic: Optionales spezifisches Thema
        max_tokens: Maximale Anzahl Tokens der Dokumentation
    
    Returns:
        Library-Informationen und Dokumentation
    """
    # Zuerst Library ID auflösen
    resolve_result = await context7.resolve_library_id(library_name)
    
    if "error" in resolve_result:
        return f"❌ Fehler beim Auflösen der Library: {resolve_result['error']}"
    
    if not resolve_result.get("libraries"):
        return f"❌ Keine Library gefunden für: {library_name}"
    
    library = resolve_result["libraries"][0]
    library_id = library.get("id")
    
    if not library_id:
        return f"❌ Keine gültige Library ID gefunden für: {library_name}"
    
    # Dann Dokumentation abrufen
    docs_result = await context7.get_library_docs(library_id, topic, max_tokens)
    
    if "error" in docs_result:
        return f"❌ Fehler beim Abrufen der Dokumentation: {docs_result['error']}"
    
    # Kombiniere Ergebnisse
    response = f"""📚 {library_name} - Dokumentation
{'='*50}

🆔 Library ID: {library_id}
📖 Beschreibung: {library.get('description', 'Keine Beschreibung verfügbar')}
⭐ Trust Score: {library.get('trustScore', 'Unbekannt')}

"""
    
    if topic:
        response += f"🎯 Thema: {topic}\n\n"
    
    if "documentation" in docs_result:
        docs = docs_result["documentation"]
        response += f"""📄 Dokumentation:
{'-'*30}
{docs[:max_tokens]}"""
        
        if len(docs) > max_tokens:
            response += f"\n\n📝 Hinweis: Dokumentation wurde auf {max_tokens} Zeichen begrenzt."
    else:
        response += "❌ Keine Dokumentation verfügbar"
    
    return response

@mcp.tool()
def server_info() -> str:
    """Gibt Informationen über den MCP Server zurück."""
    return """🚀 Context7 MCP Server (DigitalOcean)
====================================

Server Version: 2.0.0
FastMCP Version: 2.5.2
Mode: Stateless HTTP (optimiert für Cloud)

Verfügbare Tools:
• echo - Echo-Test
• hello - Begrüßung
• resolve_library - Library ID auflösen  
• get_documentation - Dokumentation abrufen
• search_and_document - Kombinierte Suche und Dokumentation
• server_info - Diese Information

🔗 Context7 Integration:
- Aktuelle Dokumentationen abrufen
- Library-Suche und ID-Auflösung
- Themen-spezifische Dokumentation

🌐 Endpoints:
- / - Service Info
- /health - Health Check
- /sse - SSE für n8n
- /mcp - Streamable HTTP (stateless)

⚡ Features:
- Stateless HTTP für bessere Skalierbarkeit
- Keine Session-Verwaltung erforderlich
- Optimiert für DigitalOcean Deployment

🏥 Status: Running"""

# ---------- ASGI App Export -------------
# Die ASGI App wird direkt in main.py erstellt mit mcp.http_app() 