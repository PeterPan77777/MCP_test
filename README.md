# Context7 MCP Server für DigitalOcean

Ein MCP (Model Context Protocol) Server mit Context7 Integration, optimiert für DigitalOcean Deployment.

## Features

- 🚀 **FastMCP 2.5.2** - Neueste Version mit verbesserter Performance
- 📚 **Context7 Integration** - Echtzeit-Zugriff auf aktuelle Library-Dokumentationen
- 🌐 **Stateless HTTP** - Optimiert für Cloud-Skalierbarkeit
- 🔧 **n8n Kompatibilität** - SSE Endpoint für n8n Integration
- ☁️ **DigitalOcean Ready** - Vorkonfiguriert für App Platform

## Endpoints

- `/` - Service-Informationen und Status
- `/health` - Health Check für Monitoring
- `/sse` - Server-Sent Events für n8n
- `/mcp` - Streamable HTTP für MCP Protokoll

## Tools

### 🔍 Library Management
- `resolve_library` - Konvertiert Library-Namen zu Context7 IDs
- `get_documentation` - Ruft Dokumentation für eine Library ab
- `search_and_document` - Kombinierte Suche und Dokumentationsabruf

### 🛠️ Utilities
- `echo` - Echo-Test Tool
- `hello` - Freundliche Begrüßung
- `server_info` - Server-Informationen

## Deployment

### DigitalOcean App Platform

1. Fork dieses Repository
2. Erstelle eine neue App in DigitalOcean
3. Wähle GitHub als Quelle
4. DigitalOcean erkennt automatisch die Konfiguration

### Lokale Entwicklung

```bash
# Clone repository
git clone https://github.com/PeterPan77777/MCP_test.git
cd MCP_test

# Installiere Dependencies
pip install -r requirements.txt

# Starte Server
python main.py
```

## Konfiguration

### Environment Variables

- `PORT` - Server Port (Standard: 8080)

### App Specification

```yaml
name: context7-mcp-server
region: fra
services:
  - name: mcp-server
    github:
      repo: PeterPan77777/MCP_test
      branch: main
    build_command: pip install -r requirements.txt
    run_command: python main.py
    envs:
      - key: PYTHON_VERSION
        value: "3.11"
    http_port: 8080
    health_check:
      http_path: /health
```

## Technologie-Stack

- **FastMCP 2.5.2** - MCP Server Framework
- **Python 3.11** - Laufzeitumgebung
- **uvicorn** - ASGI Server
- **httpx** - Async HTTP Client für Context7 API
- **Starlette** - ASGI Framework (via FastMCP)

## Version History

- **2.0.0** - Upgrade auf FastMCP 2.5.2 mit Stateless HTTP
- **1.0.0** - Initial Release mit FastMCP 2.2.9

## License

MIT

## 🚀 Features

- **FastAPI + FastMCP 2.2** - Moderne, performante MCP Server Implementation
- **Dual Transport** - SSE für n8n + streamable-http für moderne Clients
- **Context7 Integration** - Aktuelle Dokumentationen für alle Libraries abrufen
- **Docker-basiert** - Konsistente Deployments auf DigitalOcean
- **Sofortiger SSE-Handshake** - Behebt n8n Reconnect-Probleme
- **Deutsche Benutzeroberfläche** - Alle Antworten auf Deutsch

## 📁 Projekt Struktur

```
context7-mcp-server/
├── app/
│   └── main.py          # FastAPI + FastMCP + SSE Handshake
├── requirements.txt     # Python Dependencies
├── Dockerfile           # Container Build
├── app.yaml            # DigitalOcean App Platform Config
├── README.md           # Diese Dokumentation
└── deploy.md          # Detaillierte Deploy-Anleitung
```

## 📚 Verfügbare Tools

1. **echo** - Echo-Test für Verbindungscheck
2. **hello** - Freundliche Begrüßung
3. **resolve_library** - Library Namen zu Context7 ID auflösen
4. **get_documentation** - Dokumentation für Library ID abrufen
5. **search_and_document** - Kombinierte Suche und Dokumentation (⭐ BEST)
6. **server_info** - Server-Informationen anzeigen

## 🌐 Endpoints

- **`/`** - Server-Info und Status
- **`/health`** - Health Check für DigitalOcean
- **`/sse`** - Server-Sent Events (für n8n)
- **`/mcp`** - Streamable-HTTP (moderne MCP Clients)

## 🛠️ Lokale Entwicklung

### Installation

```bash
# Repository klonen
git clone https://github.com/PeterPan77777/MCP_test.git
cd MCP_test

# Virtual Environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### Server starten

```bash
# Direkt mit uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Oder mit Docker
docker build -t context7-mcp .
docker run -p 8080:8080 context7-mcp
```

### Testing

#### 1. Health Check
```bash
curl http://localhost:8080/health
# Erwartung: {"status": "ok", "service": "context7-mcp-server"}
```

#### 2. SSE Handshake (n8n kompatibel)
```bash
curl -N http://localhost:8080/sse
# Erwartung: 
# event: endpoint
# data: /messages?sessionId=...
```

#### 3. MCP Inspector

**Streamable-HTTP (empfohlen):**
```bash
npx @modelcontextprotocol/inspector
# URL: http://localhost:8080/mcp
# Transport: streamable-http
```

**SSE (n8n Modus):**
```bash
npx @modelcontextprotocol/inspector http://localhost:8080/sse
```

## 🌐 DigitalOcean Deployment

### 1. Repository vorbereiten

```bash
git add .
git commit -m "Context7 MCP Server - Docker optimiert"
git push origin main
```

### 2. DigitalOcean App erstellen

1. **DigitalOcean Dashboard:** https://cloud.digitalocean.com/
2. **Apps → Create App**
3. **GitHub Repository:** `PeterPan77777/MCP_test`
4. **Build Environment:** Docker (wird automatisch erkannt)
5. **app.yaml** wird automatisch verwendet
6. **Deploy!**

### 3. Deployment verifizieren

Nach dem Deployment (URL: `https://deine-app.ondigitalocean.app`):

```bash
# Health Check
curl https://deine-app.ondigitalocean.app/health

# SSE Handshake (muss sofort antworten!)
curl -N https://deine-app.ondigitalocean.app/sse

# MCP Inspector
npx @modelcontextprotocol/inspector https://deine-app.ondigitalocean.app/mcp
```

## 📡 n8n Integration

### Setup

1. **n8n AI Agent** erstellen
2. **MCP Server hinzufügen:**
   - **URL:** `https://deine-app.ondigitalocean.app/sse`
   - **Transport:** SSE
3. **Agent starten** - sollte sofort verbinden (kein Reconnect-Loop!)

### Verwendung

```javascript
// Schnelle Dokumentationssuche
search_and_document("react", "hooks")

// Spezifische Library
resolve_library("fastapi")
get_documentation("/tiangolo/fastapi", "authentication")

// Server-Test
echo("Hello World")
```

## 🎯 Context7 Beispiele

### React Hooks Dokumentation
```bash
search_and_document("react", "hooks")
```

### FastAPI Authentication
```bash
resolve_library("fastapi")
# Dann mit der erhaltenen Library ID:
get_documentation("/tiangolo/fastapi", "authentication")
```

### Next.js Routing
```bash
search_and_document("next.js", "routing")
```

## 🐛 Troubleshooting

### Problem: n8n Reconnect-Loop

**Symptom:** n8n verbindet sich immer wieder neu

**Lösung:** 
- Prüfe `/sse` Endpoint: `curl -N https://app.url/sse`
- Erster Frame muss sofort kommen: `event: endpoint`
- Check DigitalOcean Logs für Buffering-Probleme

### Problem: 404 auf Endpoints

**Symptom:** Alle Endpoints geben 404

**Lösung:**
1. `app.yaml` prüfen - `routes: - path: /` vorhanden?
2. Docker Build erfolgreich? Check DigitalOcean Build Logs
3. Health Check läuft? `/health` endpoint testen

### Problem: MCP Inspector "Cannot connect"

**Symptom:** Inspector zeigt Verbindungsfehler

**Lösungen:**
1. **URL Format:** `https://app.url/mcp` (für streamable-http)
2. **Transport:** Korrekt gewählt (streamable-http vs SSE)
3. **CORS:** Server sendet bereits korrekte Headers
4. **Browser Cache:** Hard Refresh (Ctrl+F5)

### Problem: Context7 API Fehler

**Symptom:** Tools returnen API-Fehler

**Debugging:**
1. **Netzwerk:** DigitalOcean erlaubt HTTPS outbound
2. **Context7 Status:** Service erreichbar?
3. **Library Namen:** Korrekte Schreibweise?

## 🔧 Performance Optimierung

### DigitalOcean Instance Size

```yaml
# app.yaml - für höhere Performance
services:
  - name: mcp-server
    instance_size_slug: basic-xs  # statt basic-xxs
```

### Context7 Timeouts

```python
# app/main.py - längere Timeouts
context7.timeout = 60.0  # statt 30.0
```

## 📊 Monitoring

### DigitalOcean Metrics

Dashboard → Apps → Deine App → **"Insights"**:
- Response Times
- HTTP Request Count  
- Memory/CPU Usage
- Error Rates

### Custom Logging

```bash
# DigitalOcean Logs anschauen
doctl apps logs <app-id> --type=build    # Build Logs
doctl apps logs <app-id> --type=deploy   # Deploy Logs  
doctl apps logs <app-id> --type=run      # Runtime Logs
```

## 🚀 Nächste Schritte

1. **Weitere Tools:** Dekoriere Funktionen mit `@mcp.tool()`
2. **Authentication:** FastMCP 2.2+ OAuth Support
3. **Caching:** Redis für Context7 Responses
4. **Monitoring:** Sentry/DataDog Integration

## 📖 Referenzen

- [FastMCP Dokumentation](https://github.com/jlowin/fastmcp)
- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [Context7 API](https://context7.dev/)
- [DigitalOcean Apps](https://docs.digitalocean.com/products/app-platform/)
- [MCP Protokoll](https://modelcontextprotocol.io/)

---

🎉 **Ready to Deploy!** Dein optimierter Context7 MCP Server läuft stabil auf DigitalOcean! 