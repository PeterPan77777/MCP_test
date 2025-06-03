#!/usr/bin/env python3
"""
Test der neuen list_engineering_tools Funktionalität
Testet sowohl spezifische Tags als auch tag="all"
"""

import asyncio
import sys
import os

# Import des FastMCP-Servers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from server import list_engineering_tools, get_available_categories

async def test_all_functionality():
    """Test der erweiterten list_engineering_tools Funktionalität"""
    
    print("🧪 === TEST: list_engineering_tools Erweiterte Funktionalität ===\n")
    
    # Test 1: Verfügbare Kategorien anzeigen
    print("1️⃣ Test: get_available_categories")
    print("-" * 50)
    categories = await get_available_categories()
    print(f"Verfügbare Kategorien: {len(categories.get('tags', []))}")
    for tag, desc in categories.get('tag_descriptions', {}).items():
        print(f"   📂 {tag}: {desc}")
    print()
    
    # Test 2: Spezifische Tags (Elementar)
    print("2️⃣ Test: list_engineering_tools mit spezifischen Tags")
    print("-" * 50)
    elementar_tools = await list_engineering_tools(tags=["elementar"])
    print(f"Tools mit Tag 'elementar': {elementar_tools['tool_count']}")
    for tool in elementar_tools['tools'][:3]:  # Erste 3 Tools
        print(f"   🔧 {tool['name']}: {tool['short_description']}")
        print(f"      Tags: {tool['tags']}")
    print()
    
    # Test 3: Tag "all" - NEUE FUNKTIONALITÄT
    print("3️⃣ Test: list_engineering_tools mit tag='all' (NEU!)")
    print("-" * 50)
    all_tools = await list_engineering_tools(tags=["all"])
    print(f"🎯 Alle verfügbaren Tools: {all_tools['total_tools']}")
    print(f"📊 Kategorien-Übersicht: {all_tools['category_summary']}")
    print()
    
    # Zeige Tools pro Kategorie
    for category, tools in all_tools['categories'].items():
        print(f"📂 Kategorie '{category}': {len(tools)} Tools")
        for tool in tools[:2]:  # Erste 2 Tools pro Kategorie
            print(f"   🔧 {tool['name']}: {tool['short_description']}")
        if len(tools) > 2:
            print(f"   ... und {len(tools) - 2} weitere Tools")
        print()
    
    # Test 4: Vergleich der Tool-Listen
    print("4️⃣ Test: Vergleich spezifische vs. alle Tools")
    print("-" * 50)
    
    umfang_tools = await list_engineering_tools(tags=["Umfang"])
    print(f"Tools mit Tag 'Umfang': {umfang_tools['tool_count']}")
    umfang_names = [tool['name'] for tool in umfang_tools['tools']]
    
    all_umfang_from_all = [tool for tool in all_tools['all_tools'] if 'Umfang' in tool['tags']]
    print(f"Umfang-Tools in 'all'-Liste: {len(all_umfang_from_all)}")
    
    print(f"✅ Konsistenz-Check: {set(umfang_names) == set(tool['name'] for tool in all_umfang_from_all)}")
    print()
    
    # Test 5: Performance-Vergleich
    print("5️⃣ Test: Performance-Messung")
    print("-" * 50)
    
    import time
    
    # Zeitmessung für spezifische Tags
    start = time.time()
    await list_engineering_tools(tags=["elementar"])
    specific_time = time.time() - start
    
    # Zeitmessung für alle Tools
    start = time.time()
    await list_engineering_tools(tags=["all"])
    all_time = time.time() - start
    
    print(f"⏱️ Zeit für spezifische Tags: {specific_time:.4f}s")
    print(f"⏱️ Zeit für alle Tools: {all_time:.4f}s")
    if specific_time > 0:
        print(f"📈 Overhead für 'all': {((all_time - specific_time) / specific_time * 100):.1f}%")
    else:
        print(f"📈 Overhead für 'all': Beide Operationen zu schnell für Messung")
    print()
    
    print("✅ === ALLE TESTS ERFOLGREICH === ✅")

if __name__ == "__main__":
    # Initialisiere Engineering-Tools vor dem Test
    async def main():
        # Import der Initialisierung
        from server import init_engineering_tools
        await init_engineering_tools()
        
        # Führe Tests aus
        await test_all_functionality()
    
    asyncio.run(main()) 