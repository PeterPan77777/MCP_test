#!/usr/bin/env python3
"""
Engineering Tool Tag Manager - Startup Script

Startet das Web-Interface für die Tag-Verwaltung.
Überprüft Abhängigkeiten und installiert diese automatisch falls nötig.
"""

import os
import sys
import subprocess
import importlib.util

def check_flask_installation():
    """Überprüft ob Flask installiert ist."""
    try:
        import flask
        return True
    except ImportError:
        return False

def install_web_dependencies():
    """Installiert Web-Abhängigkeiten falls nötig."""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements_web.txt')
    
    if os.path.exists(requirements_file):
        print("📦 Installiere Web-Interface Abhängigkeiten...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', requirements_file
            ])
            print("✅ Abhängigkeiten erfolgreich installiert")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler beim Installieren der Abhängigkeiten: {e}")
            return False
    else:
        print("⚠️ requirements_web.txt nicht gefunden")
        return False

def main():
    """Hauptfunktion - startet den Tag Manager."""
    print("🏷️ Engineering Tool Tag Manager")
    print("=" * 50)
    
    # Überprüfe Flask
    if not check_flask_installation():
        print("⚠️ Flask ist nicht installiert")
        if input("Möchten Sie Flask und die Web-Abhängigkeiten installieren? (j/n): ").lower() == 'j':
            if not install_web_dependencies():
                print("❌ Installation fehlgeschlagen. Bitte manuell installieren:")
                print("   pip install Flask")
                sys.exit(1)
        else:
            print("❌ Flask ist erforderlich. Installation abgebrochen.")
            sys.exit(1)
    
    # Importiere und starte Web-Interface
    try:
        from tag_manager_web import app
        print("🌐 Starte Web-Interface...")
        print("📍 URL: http://localhost:5000")
        print("⏹️ Drücken Sie Ctrl+C zum Beenden")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Fehler beim Importieren des Web-Interface: {e}")
        print("💡 Stellen Sie sicher, dass Sie sich im korrekten Verzeichnis befinden")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Tag Manager beendet")
    except Exception as e:
        print(f"❌ Fehler beim Starten: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 