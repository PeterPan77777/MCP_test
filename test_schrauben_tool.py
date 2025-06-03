#!/usr/bin/env python3
"""
Quick-Test für das neue Schrauben-Tool
"""

import asyncio
import sys
import os

# Import des FastMCP-Servers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from server import init_engineering_tools, list_engineering_tools, get_tool_details, call_tool

async def test_schrauben_tool():
    """Test des neuen Schrauben-Tools"""
    
    print("🧪 === TEST: Neues Schrauben-Tool ===\n")
    
    # Server initialisieren
    await init_engineering_tools()
    
    # Test 1: Alle Tools anzeigen (sollte das neue Tool enthalten)
    print("1️⃣ Test: Alle Tools mit tag='all'")
    print("-" * 50)
    all_tools = await list_engineering_tools(tags=["all"])
    print(f"🎯 Gefundene Tools insgesamt: {all_tools['total_tools']}")
    print(f"📊 Kategorien: {all_tools['category_summary']}")
    
    # Suche nach Schrauben-Tools
    schrauben_tools = [tool for tool in all_tools['all_tools'] if 'schrauben' in tool['tags']]
    print(f"🔧 Schrauben-Tools gefunden: {len(schrauben_tools)}")
    for tool in schrauben_tools:
        print(f"   - {tool['name']}: {tool['short_description']}")
    print()
    
    # Test 2: Spezifischer Tag-Filter für Schrauben
    print("2️⃣ Test: list_engineering_tools mit tag='schrauben'")
    print("-" * 50)
    schrauben_list = await list_engineering_tools(tags=["schrauben"])
    print(f"Tools mit Tag 'schrauben': {schrauben_list['tool_count']}")
    for tool in schrauben_list['tools']:
        print(f"   🔧 {tool['name']}: {tool['short_description']}")
        print(f"      Tags: {tool['tags']}")
    print()
    
    # Test 3: Tool-Details abrufen
    if schrauben_list['tool_count'] > 0:
        tool_name = schrauben_list['tools'][0]['name']
        print(f"3️⃣ Test: get_tool_details für '{tool_name}'")
        print("-" * 50)
        details = await get_tool_details(tool_name)
        print(f"✅ Tool Details erhalten:")
        print(f"   Name: {details.get('tool_name')}")
        print(f"   Beschreibung: {details.get('description', '')[:100]}...")
        print(f"   Kategorie: {details.get('category')}")
        print(f"   Berechnungstyp: {details.get('calculation_type')}")
        print(f"   Symbolische Berechnung: {details.get('has_symbolic_solving')}")
        print()
        
        # Test 4: Tool ausführen
        print(f"4️⃣ Test: call_tool für '{tool_name}'")
        print("-" * 50)
        test_params = {"screw_size": "M10", "hole_class": "mittel"}
        print(f"Parameter: {test_params}")
        
        try:
            result = await call_tool(tool_name, test_params)
            print(f"✅ Tool erfolgreich ausgeführt!")
            print(f"Status: {result.get('status')}")
            print(f"Ergebnis: {result.get('result', {}).get('diameter')}")
            print(f"Quelle: {result.get('result', {}).get('source')}")
            print(f"Typ: {result.get('result', {}).get('calculation_type')}")
        except Exception as e:
            print(f"❌ Fehler bei Tool-Ausführung: {e}")
        print()
    
    # Test 5: Tabellenwerk-Tag testen
    print("5️⃣ Test: list_engineering_tools mit tag='tabellenwerk'")
    print("-" * 50)
    tabellen_list = await list_engineering_tools(tags=["tabellenwerk"])
    print(f"Tools mit Tag 'tabellenwerk': {tabellen_list['tool_count']}")
    for tool in tabellen_list['tools']:
        print(f"   📋 {tool['name']}: {tool['short_description']}")
    print()
    
    print("✅ === SCHRAUBEN-TOOL TESTS ERFOLGREICH === ✅")

if __name__ == "__main__":
    asyncio.run(test_schrauben_tool()) 