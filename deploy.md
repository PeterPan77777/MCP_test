# DigitalOcean Deployment Anleitung

Schritt-für-Schritt Anleitung zum Deployment des Context7 MCP Servers auf DigitalOcean App Platform.

## 🚀 Schnell-Deployment (5 Minuten)

### 1. Repository auf GitHub

```bash
# Repository erstellen
git init
git add .
git commit -m "Context7 MCP Server - Initial commit"

# GitHub Repository erstellen (oder über GitHub UI)
gh repo create context7-mcp-server --public --push
```

### 2. DigitalOcean App erstellen

1. **DigitalOcean Dashboard** öffnen: https://cloud.digitalocean.com/
2. **"Apps"** im Seitenmenu wählen
3. **"Create App"** Button klicken
4. **GitHub** als Source wählen
5. **Repository** auswählen: `dein-username/context7-mcp-server`
6. **Branch**: `main`
7. **Autodeploy**: ✅ aktiviert lassen
8. **"Next"** klicken

### 3. App Konfiguration

Die `app.yaml` wird automatisch erkannt. DigitalOcean zeigt:

```yaml
✅ Service: mcp-server
✅ Environment: Python
✅ Build Command: automatisch
✅ Run Command: python server.py
✅ HTTP Port: 8080
```

**"Next"** klicken → **"Next"** klicken → **"Create Resources"** klicken

### 4. Deployment verfolgen

- **Build Logs** anschauen
- Warten bis Status: **"Running"** 
- **Live App** Link notieren: `https://your-app-name.ondigitalocean.app`

## 🧪 Testing nach Deployment

### 1. Health Check

```bash
curl -N https://your-app-name.ondigitalocean.app/sse
```

**Erwartete Antwort:**
```
event: endpoint
data: /sse

event: message  
data: {"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
```

### 2. MCP Inspector

```bash
npx @modelcontextprotocol/inspector https://your-app-name.ondigitalocean.app/sse
```

**Im Browser öffnen** → Tools testen:
- ✅ `hello` 
- ✅ `server_info`
- ✅ `search_and_document` mit "react"

## 🛠️ Alternative: doctl CLI

### 1. doctl installieren

**Windows:**
```powershell
# Über Chocolatey
choco install doctl

# Oder Download: https://github.com/digitalocean/doctl/releases
```

**Mac:**
```bash
brew install doctl
```

**Linux:**
```bash
wget https://github.com/digitalocean/doctl/releases/latest/download/doctl-*-linux-amd64.tar.gz
tar xf doctl-*-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

### 2. Authentication

```bash
# API Token erstellen: https://cloud.digitalocean.com/account/api/tokens
doctl auth init
```

### 3. App deployen

```bash
doctl apps create --spec app.yaml
```

**App ID** notieren und Status verfolgen:
```bash
doctl apps list
doctl apps get <app-id>
```

## 🐛 Troubleshooting

### Problem: 404 auf /sse

**Symptom:** `curl https://app.ondigitalocean.app/sse` → 404

**Lösung:**
1. `app.yaml` prüfen - sind Routes definiert?
2. App **neu deployen**:
   ```bash
   # Git push triggert auto-deployment
   git add app.yaml
   git commit -m "Fix routes"
   git push
   ```

### Problem: Server startet nicht

**Symptom:** App Status "Error" oder "Build Failed"

**Debugging:**
1. **Runtime Logs** in DigitalOcean Dashboard anschauen
2. Häufige Probleme:
   - Python Version zu alt → Add `runtime.txt`: `python-3.11`  
   - Dependencies fehlen → `requirements.txt` prüfen
   - Port-Bindung → Server muss auf `0.0.0.0:8080` lauschen

**Fix runtime.txt:**
```bash
echo "python-3.11" > runtime.txt
git add runtime.txt
git commit -m "Fix Python version"
git push
```

### Problem: MCP Inspector "Cannot connect"

**Symptom:** Inspector lädt nicht oder zeigt Verbindungsfehler

**Lösungen:**
1. **URL Format prüfen:** `https://app.ondigitalocean.app/sse` (HTTPS!)
2. **CORS Headers:** Server sendet bereits korrekte Headers
3. **Browser Cache:** Hard Refresh (Ctrl+F5)
4. **Network Tab** im Browser → Check for Errors

### Problem: Context7 API Fehler

**Symptom:** Tools return "Fehler beim Auflösen der Library ID"

**Debugging:**
1. Test von lokal:
   ```python
   import httpx
   httpx.get("https://api.context7.dev")  # Should work
   ```
2. DigitalOcean Firewall → sollte ausgehende HTTPS erlauben
3. Context7 Service Status prüfen

### Problem: Slow Performance

**Symptom:** Tools antworten langsam (>10s)

**Lösungen:**
1. **Instance Size erhöhen:** 
   - `app.yaml` → `instance_size_slug: basic-xs`
   - Git push für Redeploy
2. **Timeout erhöhen:**
   ```python
   # in server.py
   context7 = Context7Client()
   context7.timeout = 60.0  # statt 30.0
   ```

## 📊 Monitoring

### App Metrics

DigitalOcean Dashboard → Apps → Deine App → **"Insights"**:
- CPU Usage
- Memory Usage  
- HTTP Requests
- Response Times

### Custom Logging

Logs im Dashboard anschauen oder via CLI:
```bash
doctl apps logs <app-id> --type=run
```

**Erweiterte Logs in server.py:**
```python
import logging
logging.basicConfig(level=logging.INFO)

# Dann in den Tools:
logging.info(f"Resolving library: {library_name}")
```

## 💰 Kostenoptimierung

### Free Tier maximieren

- **basic-xxs**: $5/Monat (512MB RAM, 1 vCPU)
- **Sleeping Apps**: Für Development/Testing
- **Static Sites**: Kostenlos für Frontend

### Resources optimieren

```yaml
# app.yaml für minimal costs
services:
  - name: mcp-server
    instance_size_slug: basic-xxs    # Smallest
    instance_count: 1                # Single instance
```

## 🔄 Updates & Wartung

### Auto-Deployment

Jeder `git push` löst automatisch Rebuild + Deployment aus.

### Manual Redeploy

```bash
# Via doctl
doctl apps create-deployment <app-id>

# Via Dashboard  
Apps → Deine App → "Actions" → "Force Rebuild and Deploy"
```

### Rollback

```bash
# Letzte Deployments anzeigen
doctl apps list-deployments <app-id>

# Zu vorherigem Deployment zurück
doctl apps create-deployment <app-id> --force-rebuild
```

---

🎯 **Deployment erfolgreich!** Dein Context7 MCP Server läuft jetzt auf DigitalOcean und ist bereit für n8n Integration. 