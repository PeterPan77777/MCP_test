#!/usr/bin/env python3
"""
List Engineering Tools Meta-Tool

Listet verfügbare Engineering-Tools auf – der Einstiegspunkt für Tool‑Discovery.
Erster Schritt im 3‑stufigen Discovery‑Workflow.
"""

from typing import Dict, List, Annotated
from pydantic import Field
import asyncio
from engineering_mcp.registry import (
    get_tool_info_for_llm,
    discover_engineering_tools,
    _ENGINEERING_TOOLS_REGISTRY,
)

# Tag‑Definitionen werden LAZY geladen um Circular Imports zu vermeiden

def _create_dynamic_tags_field():
    """Erstellt ein Pydantic‑Field für den *tags*‑Parameter ohne enum‑Einschränkung."""
    try:
        from engineering_mcp.tag_definitions import get_tag_definitions

        tag_defs = get_tag_definitions()
        tag_descriptions = {
            "all": "Complete overview - Shows all available Engineering tools (full library overview)"
        }
        for tag, data in tag_defs.items():
            tag_descriptions[tag] = data["description"]

        return Field(
            description="REQUIRED: Tags for filtering tools; see 'tag_descriptions' for details",
            min_length=1,
            max_items=10,
            examples=[["all"], ["elementar"], ["mechanik"], ["schrauben"]],
            title="Engineering Tool Filter Tags",
            json_schema_extra={
                "items": {"type": "string"},
                "uniqueItems": True,
                "tag_descriptions": tag_descriptions,
                "tag_count": len(tag_descriptions),
                "format": "engineering-tag-list-with-descriptions",
                "usage_hint": "Use ['all'] for the full overview or specific tags for a filtered list",
            },
        )
    except Exception as e:
        return Field(
            description="REQUIRED: Tags for tool filtering (degraded mode)",
            min_length=1,
            max_items=10,
            examples=[["all"], ["unknown"]],
            title="Engineering Tool Filter Tags (Degraded Mode)",
            json_schema_extra={
                "items": {"type": "string"},
                "uniqueItems": True,
                "degraded_mode": True,
                "issue": f"Tag definitions not available: {e}",
            },
        )


# ------------------------------------------------------------
# Hauptfunktion: list_engineering_tools
# ------------------------------------------------------------

def list_engineering_tools(
    tags: Annotated[List[str], _create_dynamic_tags_field()]
) -> List[Dict]:
    """Gibt eine gefilterte Übersicht aller Engineering‑Tools zurück."""

    # 1) Registry sicherstellen ------------------------------------------------
    if not _ENGINEERING_TOOLS_REGISTRY:
        try:
            asyncio.run(discover_engineering_tools())
        except Exception as e:
            return [
                {
                    "error": "REGISTRY_INITIALIZATION_ERROR",
                    "problem": f"Engineering‑Tools konnten nicht geladen werden: {e}",
                    "suggestion": "Server neu starten oder Tool‑Verzeichnisse prüfen",
                    "workflow_step": "1/3 - System‑Fehler",
                }
            ]

    # 2) Parameter validieren --------------------------------------------------
    if not tags:
        try:
            from engineering_mcp.tag_definitions import get_tag_definitions
            tag_defs = get_tag_definitions()
            available_tags = ["all"] + sorted(tag_defs.keys()) if tag_defs else ["all"]
        except Exception:
            available_tags = ["all", "unknown"]
        examples = [f"list_engineering_tools(tags=['{t}'])" for t in (available_tags[:4] or ["all"])]

        return [
            {
                "error": "INVALID_TOOL_USAGE",
                "problem": "list_engineering_tools() ohne tags‑Parameter aufgerufen",
                "required_parameter": "tags",
                "available_tags": available_tags,
                "correct_usage": examples,
                "workflow_step": "1/3 - Ungültige Verwendung",
            }
        ]

    # 3) Tools laden & filtern -------------------------------------------------
    all_tools = get_tool_info_for_llm(include_engineering=True)
    if "all" in tags:
        result_tools = all_tools
    else:
        result_tools = [t for t in all_tools if any(tag in t.get("tags", []) for tag in tags)]

    if not result_tools and all_tools:
        try:
            from engineering_mcp.tag_definitions import get_tag_definitions
            tag_defs = get_tag_definitions()
            available_tags = ["all"] + sorted(tag_defs.keys()) if tag_defs else ["all"]
        except Exception:
            available_tags = ["all", "unknown"]

        return [
            {
                "warning": "NO_TOOLS_FOUND",
                "tags_searched": tags,
                "total_tools_available": len(all_tools),
                "available_tags": available_tags,
                "suggestion": "Andere Tags verwenden oder tags=['all'] versuchen",
                "workflow_step": "1/3 - Keine Treffer",
            }
        ]

    # 4) Erfolgreiche Antwort ---------------------------------------------------
    tools_output = [
        {
            "name": t["name"],
            "short_description": t.get("short_description", ""),
            "tags": t.get("tags", []),
            "has_solving": t.get("has_solving", "symbolic"),
        }
        for t in result_tools
    ]

    return [
        {
            "status": "SUCCESS",
            "message": f"{len(result_tools)} Tools gefunden",
            "step": "1/3",
            "workflow_guidance": [
                "1. list_engineering_tools(tags=[...]) – erledigt",
                "2. get_tool_details(tool_name='...') – Details abrufen",
                "3. call_tool(tool_name='...', parameters={...}) – Tool ausführen",
            ],
            "tools": tools_output,
            "total_count": len(result_tools),
            "tags_used": tags,
        }
    ]


# ------------------------------------------------------------
# Tool‑Metadaten
# ------------------------------------------------------------
TOOL_METADATA = {
    "name": "1_list_engineering_tools",
    "description": """
    Listet alle verfügbaren Engineering‑Tools auf.
    Es ist nicht notwendig, dieses Tool aufzurufen, wenn Du bereits weißt, welches Tool Du aufrufen möchtest.
    
    Für eine Liste aller verfügbaren Tags dieser Funktion mindestens einmal pro Konversation mit leeren tag (tags=[""]) aufrufen, um eine vollständige Tag-Liste zu erhalten.
    
    TAG-VERWENDUNG:
    • Alle verfügbaren Tags anzeigen: tags=[""] (leer)
    • Vollständige Tool‑Übersicht: tags=["all"]
    • Einzelner Tag: tags=["mechanik"]
    • Mehrere Tags: tags=["schrauben", "DIN 13"]

WICHTIGER HINWEIS:
Verwenden Sie NIEMALS geratene Tags! Rufen zuerst tags=[""] auf um alle verfügbaren Tags zu sehen. Verwende ausschließlich angezeigte Tags.
""",
    "tags": ["meta"],
}
