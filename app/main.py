"""
Context7 MCP Server mit FastAPI + FastMCP - optimiert für DigitalOcean & n8n
"""
import uuid
import asyncio
import httpx
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastmcp import FastMCP

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
mcp = FastMCP(
    name="Context7-DO-Server",
    instructions="Context7 MCP Server optimiert für DigitalOcean und n8n"
)

@mcp.tool()
def echo(text: str) -> str:
    """Einfaches Echo-Tool zum Testen."""
    return f"Echo: {text}"

@mcp.tool()
def hello(name: str = "World") -> str:
    """Freundliche Begrüßung."""
    return f"👋 Hallo, {name}! Context7 MCP Server läuft!"

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

🌐 Transports:
- SSE: /sse (für n8n)
- streamable-http: /mcp (modern)

🏥 Health Check: /health"""

# ---------- FastAPI App -------------
app = FastAPI(title="Context7 MCP Server", version="1.0.0")

# Modernes streamable-HTTP unter /mcp (FastMCP 2.2 korrekte API)
mcp_app = mcp.http_app(path="/mcp")
app.mount("/mcp", mcp_app)

@app.get("/health")
async def health():
    """Health Check für DigitalOcean"""
    return JSONResponse({"status": "ok", "service": "context7-mcp-server"})

# --------- SSE für n8n ----------
async def sse_gen():
    """
    N8n-kompatibler SSE Handshake:
        event: endpoint
        data: /messages?sessionId=<uuid>
    Danach Keep-alive Pings alle 15s
    """
    sid = uuid.uuid4().hex
    
    # 1. Handshake-Frame (sofort!)
    yield f"event: endpoint\ndata: /messages?sessionId={sid}\n\n"
    
    # 2. Optional: done-Frame (wie Context7)
    yield f"event: done\ndata: {{\"type\":\"done\",\"client_id\":\"{sid}\"}}\n\n"
    
    # 3. Keep-alive-Pings (alle 15s)
    while True:
        await asyncio.sleep(15)
        yield ": ping\n\n"

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE Endpoint für n8n MCP Client"""
    headers = {
        "Cache-Control": "no-cache, no-transform",  # Verhindert Proxy-Buffering
        "Content-Type": "text/event-stream",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return StreamingResponse(sse_gen(), headers=headers)

# Root endpoint
@app.get("/")
async def root():
    return JSONResponse({
        "service": "Context7 MCP Server",
        "endpoints": {
            "health": "/health",
            "sse": "/sse (für n8n)",
            "mcp": "/mcp (streamable-http)",
        },
        "status": "running"
    }) 