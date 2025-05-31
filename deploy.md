# DigitalOcean Deployment Anleitung (Docker)

Optimierte Schritt-für-Schritt Anleitung für den Context7 MCP Server mit FastAPI + FastMCP auf DigitalOcean App Platform.

## 🚀 Schnell-Deployment (5 Minuten)

### 1. Repository Push

```bash
# Alle Änderungen committen
git add .
git commit -m "Context7 MCP Server - Docker optimiert für DigitalOcean"

# Push zu GitHub
git push origin main
```

### 2. DigitalOcean App erstellen

1. **DigitalOcean Dashboard:** https://cloud.digitalocean.com/
2. **"Apps"** → **"Create App"**
3. **GitHub** als Source wählen
4. **Repository:** `PeterPan77777/MCP_test` auswählen
5. **Branch:** `main`
6. **Autodeploy:** ✅ aktiviert lassen

### 3. Build-Erkennung

DigitalOcean erkennt automatisch:
```
✅ Dockerfile gefunden
✅ Environment: Docker
✅ Port: 8080 (aus Dockerfile)
✅ app.yaml Konfiguration erkannt
```

### 4. Deployment überwachen

- **Build Logs** anschauen: Dockerfile wird ausgeführt
- **Deploy Logs:** FastAPI Server startet
- **Status:** Warten auf **"Running"**
- **URL notieren:** `https://context7-mcp-server-xxx.ondigitalocean.app`

## ✅ Sofort-Verifikation

### 1. Health Check (muss sofort funktionieren)

```bash
curl https://deine-app.ondigitalocean.app/health
```

**Erwartete Antwort:**
```json
{"status": "ok", "service": "context7-mcp-server"}
```

### 2. SSE Handshake (kritisch für n8n!)

```bash
curl -N https://deine-app.ondigitalocean.app/sse
```

**Erwartete Antwort (sofort, keine Verzögerung!):**
```
event: endpoint
data: /messages?sessionId=abc123...

event: done
data: {"type":"done","client_id":"abc123..."}

: ping
```

### 3. MCP Inspector Test

```bash
npx @modelcontextprotocol/inspector
```

**Im Browser:**
- **Transport:** `streamable-http`
- **URL:** `https://deine-app.ondigitalocean.app/mcp`
- **Test:** `echo` Tool mit "Hello Test"

## 📡 n8n Integration Test

1. **n8n öffnen** (lokal oder Cloud)
2. **AI Agent Node** erstellen
3. **MCP Server konfigurieren:**
   ```
   URL: https://deine-app.ondigitalocean.app/sse
   Transport: SSE
   ```
4. **Verbindung testen** - sollte **sofort** verbinden!
5. **Tool ausführen:** `search_and_document("react", "hooks")`

## 🛠️ Alternative: CLI Deployment

### 1. doctl Setup

```bash
# doctl installieren (falls noch nicht vorhanden)
# Windows: choco install doctl
# Mac: brew install doctl
# Linux: wget + extract

# Authentifizierung
doctl auth init
# API Token: https://cloud.digitalocean.com/account/api/tokens
```

### 2. App via CLI deployen

```bash
# App erstellen
doctl apps create --spec app.yaml

# Status verfolgen
doctl apps list
doctl apps get <app-id>

# Logs anschauen
doctl apps logs <app-id> --type=build
doctl apps logs <app-id> --type=deploy
doctl apps logs <app-id> --type=run
```

## 🐛 Troubleshooting Guide

### Problem: Docker Build Failed

**Symptom:** Build bricht ab mit Fehlern

**Debug Steps:**
1. **Build Logs prüfen** in DigitalOcean Dashboard
2. **Lokaler Test:**
   ```bash
   docker build -t test-mcp .
   docker run -p 8080:8080 test-mcp
   ```
3. **Häufige Ursachen:**
   - `requirements.txt` fehlt/falsch
   - Python Version nicht kompatibel
   - `app/main.py` Pfad falsch

**Fix:**
```bash
# Lokaler Test vor Push
docker build -t context7-mcp .
docker run -p 8080:8080 context7-mcp
# Test: curl http://localhost:8080/health
```

### Problem: App startet nicht (Port Binding)

**Symptom:** "Application failed to start" nach Build

**Debug:**
```bash
# DigitalOcean Logs anschauen
doctl apps logs <app-id> --type=run
```

**Häufige Fehler:**
```
❌ uvicorn: error: unrecognized arguments: --port $PORT
❌ Address already in use
❌ ModuleNotFoundError: No module named 'app'
```

**Fix in Dockerfile:**
```dockerfile
# Stelle sicher, dass Port 8080 hardcoded ist
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Problem: SSE Connection sofort schließt

**Symptom:** n8n/Inspector reconnectet sofort

**Debug:**
```bash
# SSE Stream testen
curl -v -N https://app.url/sse

# Prüfe Response Headers:
< Content-Type: text/event-stream
< Cache-Control: no-cache, no-transform
< Connection: keep-alive
```

**Typische Ursachen:**
- Erster `event: endpoint` Frame zu spät
- Proxy buffering (fehlender `no-transform` Header)
- Async Generator Probleme

**Fix prüfen in app/main.py:**
```python
# sse_gen() muss sofort yielden:
yield f"event: endpoint\ndata: /messages?sessionId={sid}\n\n"
```

### Problem: 404 auf allen Endpoints

**Symptom:** Alle URLs geben 404, auch `/health`

**Ursache:** `routes:` fehlt in `app.yaml`

**Fix app.yaml:**
```yaml
services:
  - name: mcp-server
    routes:           # 👈 KRITISCH!
      - path: /
```

### Problem: Context7 API nicht erreichbar

**Symptom:** Tools returnen "Fehler beim Auflösen der Library ID"

**Debug:**
1. **Lokaler Test:**
   ```python
   import httpx
   httpx.get("https://api.context7.dev")
   ```

2. **DigitalOcean Firewall:** Outbound HTTPS erlaubt?

3. **DNS Resolution:** Context7 erreichbar?

**Fix:** Timeout in `app/main.py` erhöhen:
```python
context7.timeout = 60.0  # statt 30.0
```

### Problem: Slow Performance / Timeouts

**Symptom:** Tools antworten sehr langsam (>30s)

**Lösungen:**

1. **Instance Size erhöhen:**
   ```yaml
   # app.yaml
   instance_size_slug: basic-xs  # statt basic-xxs
   ```

2. **Request Timeouts optimieren:**
   ```python
   # app/main.py
   context7.timeout = 45.0
   max_tokens = 5000  # weniger Daten
   ```

3. **HTTP Connection Pooling:**
   ```python
   # Persistent HTTP Client
   http_client = httpx.AsyncClient(timeout=60.0)
   ```

## 📊 Monitoring & Observability

### DigitalOcean App Insights

Dashboard → Apps → Deine App → **"Insights"**:
- 🚀 **Response Time:** < 2s normal
- 📊 **Request Rate:** Anzahl MCP calls
- 💾 **Memory Usage:** < 80% bei basic-xxs
- ⚡ **CPU Usage:** Spikes bei Context7 calls

### Logs Monitoring

```bash
# Live Logs verfolgen
doctl apps logs <app-id> --type=run --follow

# Fehler filtern
doctl apps logs <app-id> --type=run | grep -i error

# Performance Debugging
doctl apps logs <app-id> --type=run | grep -E "(POST|GET|ERROR)"
```

### Custom Alerts

**App.yaml erweitern:**
```yaml
alerts:
  - rule: CPU_UTILIZATION
    value: 80
  - rule: MEMORY_UTILIZATION  
    value: 90
```

## 💰 Kostenoptimierung

### Minimale Konfiguration

```yaml
# app.yaml - für Development
services:
  - name: mcp-server
    instance_size_slug: basic-xxs    # $5/Monat
    instance_count: 1                # Keine Redundanz
```

### Production Setup

```yaml
# app.yaml - für Production
services:
  - name: mcp-server
    instance_size_slug: basic-xs     # $12/Monat
    instance_count: 2                # Redundanz
```

## 🔄 Updates & Maintenance

### Auto-Deployment

Jeder Push zu `main` triggert automatisch:
1. 🔨 **Docker Build** (ca. 2-3 Min)
2. 🚀 **Deploy** (ca. 1 Min)  
3. ✅ **Health Check** 
4. 🌐 **Live Traffic** Switch

### Manual Redeploy

```bash
# Force rebuild (ohne Code-Änderungen)
doctl apps create-deployment <app-id> --force-rebuild

# Oder im Dashboard:
# Apps → Deine App → "Actions" → "Force Rebuild and Deploy"
```

### Rollback Strategy

```bash
# Vorherige Deployments anzeigen
doctl apps list-deployments <app-id>

# Zu spezifischem Deployment zurück
doctl apps create-deployment <app-id> --deployment-id <previous-deployment-id>
```

## 🎯 Production Checklist

Vor Go-Live prüfen:

- ✅ **Health Check:** `/health` antwortet schnell
- ✅ **SSE Handshake:** Erster Frame < 500ms
- ✅ **MCP Inspector:** Alle Tools funktionieren  
- ✅ **n8n Integration:** Keine Reconnect-Loops
- ✅ **Context7 API:** Library-Suche funktioniert
- ✅ **Performance:** Response Times < 5s
- ✅ **Monitoring:** Logs/Metrics konfiguriert
- ✅ **Backups:** Repository + Config gesichert

---

🎉 **Deployment Complete!** Dein Context7 MCP Server läuft stabil und optimiert auf DigitalOcean! 