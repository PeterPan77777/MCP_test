import asyncio
import httpx
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# MCP Server mit Context7 Integration
mcp = FastMCP(
    name="Context7-MCP-Server",
    instructions="Ein FastMCP Server mit Context7 Integration für aktuelle Dokumentationsabfrage."
)

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

@mcp.tool()
def hello(name: str = "World") -> str:
    """Gibt eine freundliche Begrüßung zurück."""
    return f"👋 Hallo, {name}! Willkommen zum Context7 MCP Server!"

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
        library = result["libraries"][0]  # Nehme die erste/beste Übereinstimmung
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
        
        # Strukturiere die Antwort
        response = f"""📚 Dokumentation für {library_id}
{'='*50}

"""
        
        if topic:
            response += f"🎯 Thema: {topic}\n\n"
        
        response += docs[:max_tokens]  # Begrenze die Ausgabe
        
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
    return """🚀 Context7 MCP Server
================================

Verfügbare Tools:
• hello - Begrüßung
• resolve_library - Library ID auflösen  
• get_documentation - Dokumentation abrufen
• search_and_document - Kombinierte Suche und Dokumentation
• server_info - Diese Information

🔗 Context7 Integration:
- Aktuelle Dokumentationen abrufen
- Library-Suche und ID-Auflösung
- Themen-spezifische Dokumentation

🌐 Deployment: DigitalOcean App Platform ready
📡 Transport: Server-Sent Events (SSE)"""

# Health Check Endpoint
@mcp.tool()
def health_check() -> str:
    """Health Check für DigitalOcean"""
    return "✅ Server läuft korrekt"

# Entry-Point für DigitalOcean
if __name__ == "__main__":
    # SSE Transport für n8n/MCP-Inspector auf /sse
    print("🚀 Starte Context7 MCP Server...")
    print("📡 SSE Transport: http://0.0.0.0:8080/sse")
    print("🔍 MCP Inspector: npx @modelcontextprotocol/inspector http://localhost:8080/sse")
    
    mcp.run(transport="sse", host="0.0.0.0", port=8080, path="/sse") 