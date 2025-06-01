# Simple MCP Server

Ein minimaler MCP (Model Context Protocol) Server mit SSE und HTTP Streamable Support.

## Features

- ✅ Streamable HTTP Transport
- ✅ SSE Transport (Legacy)
- ✅ Railway-ready
- ✅ MCP Inspector kompatibel

## Tools

1. **echo** - Gibt eine Nachricht zurück
2. **calculate** - Evaluiert mathematische Ausdrücke
3. **server_info** - Zeigt Server-Informationen

## Lokale Entwicklung

### 1. Installation

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Mac/Linux)
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Server starten

**Option A: Stdio Mode (für lokale Tests)**
```bash
python server.py
```

**Option B: HTTP Mode (für MCP Inspector)**
```bash
python web.py
```

### 3. Mit MCP Inspector testen

```bash
# Installiere MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Teste mit Streamable HTTP (empfohlen)
npx @modelcontextprotocol/inspector http://localhost:8080/mcp

# Oder teste mit SSE
npx @modelcontextprotocol/inspector http://localhost:8080/sse
```

## Railway Deployment

### 1. Repository vorbereiten

```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Auf GitHub pushen

```bash
# Erstelle ein neues Repository auf GitHub
# Dann:
git remote add origin https://github.com/DEIN_USERNAME/DEIN_REPO.git
git push -u origin main
```

### 3. Railway Deployment

```bash
# Railway CLI installieren
npm install -g @railway/cli

# Login
railway login

# Neues Projekt erstellen
railway init

# Deployen
railway up
```

Oder über das Railway Dashboard:
1. Gehe zu https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Wähle dein Repository
4. Railway deployed automatisch!

### 4. Railway URL erhalten

Nach dem Deployment:
```bash
railway domain
```

## MCP Inspector mit Railway

```bash
# Ersetze YOUR_APP mit deiner Railway URL
npx @modelcontextprotocol/inspector https://YOUR_APP.railway.app/mcp
```

## Projekt Struktur

```
simple-mcp-server/
├── server.py          # MCP Server Logik
├── web.py            # Web Runner für HTTP/SSE
├── requirements.txt  # Python Dependencies
├── railway.json      # Railway Config
└── README.md        # Diese Datei
```

## Troubleshooting

**Problem: MCP Inspector kann nicht verbinden**
- Stelle sicher, dass der Server läuft (`python web.py`)
- Verwende die richtige URL (mit `/mcp` am Ende)
- Prüfe die Konsole für Fehler

**Problem: Railway Deployment fehlgeschlagen**
- Check die Build Logs in Railway
- Stelle sicher, dass alle Files committed sind
- Python Version sollte 3.9+ sein

## Lizenz

MIT 