# Context7 MCP Server

Ein Model Context Protocol (MCP) Server basierend auf FastMCP mit Context7 Integration für aktuelle Dokumentationsabfrage.

## 🚀 Features

- **FastMCP 2.x** - Moderne MCP Server Implementation
- **Context7 Integration** - Aktuelle Dokumentationen abrufen
- **Server-Sent Events (SSE)** - Kompatibel mit n8n und MCP Inspector
- **DigitalOcean Ready** - Vorbereitet für App Platform Deployment
- **Deutsche Benutzeroberfläche** - Alle Antworten auf Deutsch

## 📚 Verfügbare Tools

1. **hello** - Freundliche Begrüßung
2. **resolve_library** - Library Namen zu Context7 ID auflösen
3. **get_documentation** - Dokumentation für Library ID abrufen
4. **search_and_document** - Kombinierte Suche und Dokumentation
5. **server_info** - Server-Informationen anzeigen
6. **health_check** - Health Check für Monitoring

## 🛠️ Lokale Entwicklung

### Voraussetzungen

- Python 3.8+
- pip

### Installation

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### Server starten

```bash
python server.py
```

Der Server läuft dann auf `http://localhost:8080/sse`

### Testing mit MCP Inspector

```bash
# MCP Inspector starten
npx @modelcontextprotocol/inspector http://127.0.0.1:8080/sse
```

Öffne den Browser und teste die Tools in der Inspector UI.

## 🌐 DigitalOcean Deployment

### 1. Repository vorbereiten

```bash
git init
git add .
git commit -m "Initial Context7 MCP Server"
git remote add origin <dein-github-repo>
git push -u origin main
```

### 2. DigitalOcean App erstellen

#### Option A: GitHub Integration (Empfohlen)

1. DigitalOcean Dashboard öffnen
2. "Apps" → "Create App"
3. GitHub Repository auswählen
4. `app.yaml` wird automatisch erkannt
5. Deploy!

#### Option B: doctl CLI

```bash
# DigitalOcean CLI installieren
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# App erstellen
doctl apps create --spec app.yaml
```

### 3. Deployment verifizieren

Nach dem Deployment (URL: https://deine-app.ondigitalocean.app):

```bash
# Health Check
curl https://deine-app.ondigitalocean.app/sse

# MCP Inspector
npx @modelcontextprotocol/inspector https://deine-app.ondigitalocean.app/sse
```

## 🔧 Context7 Verwendung

### Beispiel: React Dokumentation

```bash
# In MCP Inspector oder n8n:
search_and_document("react", "hooks")
```

### Beispiel: FastAPI Dokumentation

```bash
# Schritt 1: Library ID finden
resolve_library("fastapi")

# Schritt 2: Dokumentation abrufen  
get_documentation("/tiangolo/fastapi", "authentication")
```

## 📡 n8n Integration

1. n8n Workflow erstellen
2. MCP Client Node hinzufügen
3. Server URL: `https://deine-app.ondigitalocean.app/sse`
4. Tools verwenden:
   - `search_and_document` für schnelle Dokumentationssuche
   - `resolve_library` + `get_documentation` für detaillierte Abfragen

## 🐛 Troubleshooting

### 404 Fehler
- Überprüfe `routes` in `app.yaml`
- Stelle sicher, dass `/sse` Route existiert

### MCP Inspector Verbindungsprobleme
- Verwende nur die Basis-URL ohne zusätzliche Parameter
- Format: `http://localhost:8080/sse` (nicht `/sse?...`)

### Context7 API Fehler
- Überprüfe Internetverbindung
- Context7 Service Status prüfen
- Library Namen korrekt schreiben

### DigitalOcean Deployment Probleme
- Logs anschauen: App Dashboard → Runtime Logs
- Health Check Status prüfen
- Environment Variables überprüfen

## 📁 Projekt Struktur

```
MCP_server_TEST/
├── server.py          # Hauptserver mit FastMCP + Context7
├── requirements.txt   # Python Dependencies
├── Procfile          # DigitalOcean Start Command
├── app.yaml          # DigitalOcean App Konfiguration  
└── README.md         # Diese Dokumentation
```

## 🚀 Nächste Schritte

1. **Weitere Tools hinzufügen**: Dekoriere Funktionen mit `@mcp.tool()`
2. **Testing**: Nutze FastMCP's in-memory Client für pytest
3. **Authentifizierung**: FastMCP 2.2+ OAuth Support für Bearer Tokens
4. **Monitoring**: DigitalOcean App Metrics für Performance-Überwachung

## 📖 Referenzen

- [FastMCP Dokumentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Context7 API](https://context7.dev/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)

---

🎉 **Happy Coding!** Dein Context7 MCP Server ist bereit für die Welt! 