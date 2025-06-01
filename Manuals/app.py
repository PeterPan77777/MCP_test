"""
MCP Engineering Server - Entry Point

Haupteinstiegspunkt für den modularen MCP-Server für Ingenieurberechnungen.
Initialisiert FastMCP, lädt Konfiguration und registriert alle Tools automatisch.
"""

import os
import asyncio
from typing import Optional, Dict, List

from fastmcp import FastMCP, Context
from engineering_mcp.config import get_server_config
from engineering_mcp.registry import discover_tools, get_tool_info_for_llm, get_symbolic_tools_summary


def create_mcp_server() -> Optional[FastMCP]:
    """
    Erstellt und konfiguriert den FastMCP-Server.
    
    Returns:
        FastMCP: Konfigurierte Server-Instanz oder None bei Fehlern
    """
    # Server-Konfiguration laden
    config = get_server_config()
    server_name = config.server_name
    debug = config.debug
    
    # FastMCP-Server initialisieren
    mcp = FastMCP(
        name=server_name,
        version="0.1.0",
        docs_url="/mcp/docs" if debug else None,
        openapi_url="/mcp/openapi.json" if debug else None
    )
    
    print(f"✅ {server_name} v0.1.0 initialisiert")
    return mcp


# Globale Server-Instanz
mcp = create_mcp_server()


# Discovery-Tools als MCP-Tools registrieren
@mcp.tool(
    name="list_engineering_tools",
    description="Listet alle verfügbaren Engineering-Tools mit lösbaren Variablen auf. Verfügbare Kategorien: pressure, geometry, materials, thermodynamics, statics",
    tags=["discovery", "engineering", "meta"]
)
async def list_engineering_tools(
    category: Optional[str] = None,
    ctx: Context = None
) -> List[Dict]:
    """
    Listet alle verfügbaren Engineering-Tools mit ihren lösbaren Variablen auf.
    
    Args:
        category: Optional Kategorie-Filter (z.B. "pressure", "geometry")
        ctx: FastMCP Context für Logging
        
    Returns:
        List[Dict]: Tools mit Namen, Beschreibung, Tags und lösbaren Variablen
    """
    if ctx:
        await ctx.info("Sammle Engineering-Tool-Informationen...")
    
    # Hole Engineering-Tools aus separater Registry (NICHT von MCP!)
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    # Filter nach Kategorie wenn angegeben
    if category:
        tool_info = [tool for tool in tool_info if category in tool.get("tags", []) or category == tool.get("category")]
    
    if ctx:
        await ctx.info(f"Gefunden: {len(tool_info)} Engineering-Tools")
    
    return tool_info

@mcp.tool(
    name="get_symbolic_tools_overview",
    description="Gibt eine Übersicht aller symbolischen Tools für LLM-Orchestrierung zurück",
    tags=["discovery", "engineering", "symbolic", "meta"]
)
async def get_symbolic_tools_overview(
    ctx: Context = None
) -> Dict:
    """
    Erstellt eine strukturierte Übersicht aller symbolischen Engineering-Tools.
    
    Args:
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Kategorisierte Übersicht mit Formeln und lösbaren Variablen
    """
    if ctx:
        await ctx.info("Erstelle symbolische Tools-Übersicht...")
    
    # Hole Engineering-Tools aus separater Registry
    summary = get_symbolic_tools_summary()
    
    if ctx:
        await ctx.info(f"Übersicht erstellt: {summary.get('total_tools', 0)} symbolische Tools")
    
    return summary

@mcp.tool(
    name="suggest_tool_for_variables",
    description="Schlägt passende Tools basierend auf gegebenen/gesuchten Variablen vor",
    tags=["discovery", "engineering", "recommendation"]
)
async def suggest_tool_for_variables(
    known_variables: List[str],
    unknown_variable: str,
    ctx: Context = None
) -> List[Dict]:
    """
    Schlägt passende Tools vor, die gegebene bekannte Variablen verwenden können.
    
    Args:
        known_variables: Liste der bekannten Variablen
        unknown_variable: Gesuchte Variable
        ctx: FastMCP Context für Logging
        
    Returns:
        List[Dict]: Passende Tools mit Begründung
    """
    if ctx:
        await ctx.info(f"Suche Tools für {unknown_variable} mit bekannten Variablen: {known_variables}")
    
    suggestions = []
    
    # Hole Engineering-Tools aus separater Registry
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    for tool in tool_info:
        solvable_vars = tool.get("solvable_variables", [])
        
        # Check ob das Tool die gesuchte Variable lösen kann
        if unknown_variable in solvable_vars:
            # Check ob alle bekannten Variablen im Tool verfügbar sind
            available_vars = set(solvable_vars)
            required_vars = set(known_variables + [unknown_variable])
            
            if required_vars.issubset(available_vars):
                # Check ob genau die richtige Anzahl Variablen gegeben ist
                if len(known_variables) == len(solvable_vars) - 1:
                    suggestions.append({
                        "tool_name": tool["name"],
                        "description": tool["description"],
                        "solvable_variables": solvable_vars,
                        "reason": f"Kann {unknown_variable} aus {known_variables} berechnen",
                        "confidence": "high"
                    })
    
    if ctx:
        await ctx.info(f"Gefunden: {len(suggestions)} passende Tools")
    
    return suggestions

@mcp.tool(
    name="calculate_engineering",
    description="Führt Engineering-Berechnungen über die separate Tool-Registry aus",
    tags=["engineering", "execution", "gateway"]
)
async def calculate_engineering(
    tool_name: str,
    parameters: Dict,
    ctx: Context = None
) -> Dict:
    """
    Gateway-Funktion für Engineering-Tool-Ausführung.
    
    Args:
        tool_name: Name des Engineering-Tools
        parameters: Tool-Parameter als Dictionary
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis
        
    Raises:
        ValueError: Bei ungültigen Tools oder Parametern
    """
    if ctx:
        await ctx.info(f"Führe Engineering-Berechnung aus: {tool_name}")
        await ctx.info(f"Parameter: {parameters}")
    
    from engineering_mcp.registry import call_engineering_tool
    
    try:
        result = await call_engineering_tool(tool_name, parameters)
        
        if ctx:
            await ctx.info(f"Berechnung erfolgreich abgeschlossen")
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Fehler bei Engineering-Berechnung '{tool_name}': {e}"
        if ctx:
            await ctx.error(error_msg)
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "error": str(e),
            "status": "error"
        }

@mcp.tool(
    name="get_available_categories",
    description="Gibt alle verfügbaren Engineering-Tool-Kategorien für die Discovery zurück",
    tags=["discovery", "categories", "meta"]
)
async def get_available_categories(
    ctx: Context = None
) -> Dict:
    """
    Listet alle verfügbaren Kategorien von Engineering-Tools auf.
    
    Args:
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Kategorien mit Tool-Anzahl und Beschreibungen
    """
    if ctx:
        await ctx.info("Sammle verfügbare Tool-Kategorien...")
    
    # Hole Engineering-Tools aus Registry
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    # Gruppiere nach Kategorien
    categories_info = {}
    
    for tool in tool_info:
        category = tool.get("category", "unknown")
        
        if category not in categories_info:
            categories_info[category] = {
                "name": category,
                "tools": [],
                "tool_count": 0,
                "description": ""
            }
        
        categories_info[category]["tools"].append(tool["name"])
        categories_info[category]["tool_count"] += 1
    
    # Kategorie-Beschreibungen hinzufügen
    category_descriptions = {
        "pressure": "Druckbehälter, Kesselformeln, Druckberechnungen",
        "geometry": "Flächenberechnungen, Volumen, geometrische Formeln", 
        "materials": "Werkstoffkennwerte, Festigkeitsberechnungen",
        "thermodynamics": "Wärmeübertragung, Zustandsänderungen",
        "statics": "Statik, Kräfte, Momente, Balkenberechnung"
    }
    
    for category, info in categories_info.items():
        info["description"] = category_descriptions.get(category, f"{category.title()}-bezogene Engineering-Tools")
    
    if ctx:
        await ctx.info(f"Gefunden: {len(categories_info)} Kategorien")
    
    return {
        "available_categories": list(categories_info.keys()),
        "category_details": categories_info,
        "total_categories": len(categories_info),
        "usage_hint": "Verwende diese Kategorien mit list_engineering_tools(category='...')"
    }


async def setup_server(mcp_instance: FastMCP) -> int:
    """
    Initialisiert Server und registriert nur Meta-Tools bei MCP.
    Engineering-Tools werden separat entdeckt aber NICHT bei MCP registriert.
    
    Args:
        mcp_instance: FastMCP Server-Instanz
        
    Returns:
        int: Anzahl der registrierten Meta-Tools (5)
    """
    from engineering_mcp.registry import discover_engineering_tools
    
    # Engineering-Tools separat entdecken (NICHT bei MCP registrieren!)
    engineering_tools_count = await discover_engineering_tools()
    print(f"✅ {engineering_tools_count} Engineering-Tools entdeckt (separat gespeichert)")
    
    # Nur Meta-Tools sind bei MCP registriert (5 Tools)
    meta_tools_count = 5  # list_engineering_tools, get_symbolic_tools_overview, suggest_tool_for_variables, calculate_engineering, get_available_categories
    print(f"✅ {meta_tools_count} Meta-Tools bei MCP registriert")
    
    print(f"🎯 Zweistufige Architektur aktiviert:")
    print(f"   └─ LLM sieht nur {meta_tools_count} Meta-Tools")
    print(f"   └─ {engineering_tools_count} Engineering-Tools über Meta-Tools abrufbar")
    
    return meta_tools_count


async def main():
    """Hauptfunktion für direkten Server-Start"""
    # Server setup
    tools_count = await setup_server(mcp)
    
    if tools_count > 0:
        print(f"🚀 {mcp.name} bereit mit {tools_count} Tools")
    else:
        print("⚠️ Keine Tools geladen - Server läuft im Basis-Modus")
    
    # Für direkten uvicorn-Start
    if os.getenv("DIRECT_START"):
        try:
            import uvicorn
            
            config = get_server_config()
            port = config.port
            debug = config.debug
            
            print(f"🌐 Starte HTTP-Server auf Port {port}")
            uvicorn.run(
                "app:mcp.app",
                host="0.0.0.0",
                port=port,
                log_level="info",
                reload=debug
            )
        except ImportError:
            print("❌ uvicorn nicht verfügbar - verwende 'fastmcp dev app.py'")
        except Exception as e:
            print(f"❌ Server-Start fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Für FastMCP CLI
    asyncio.run(main()) 