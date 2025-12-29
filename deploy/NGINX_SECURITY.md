# Nginx Security Configuration

## Problem

Control-Plane, Langfuse und Grafana sind ohne Authentication/ACL erreichbar, wenn nginx öffentlich exponiert ist.

## Lösung

### Option 1: Basic Auth (Empfohlen für Production)

1. **Htpasswd-Datei erstellen:**
```bash
# Mit Docker (httpd image)
docker run --rm httpd:2.4-alpine htpasswd -nbB admin 'your-strong-password' > deploy/nginx.htpasswd

# Oder mit htpasswd (wenn installiert)
htpasswd -cB deploy/nginx.htpasswd admin
```

**WICHTIG:** `deploy/nginx.htpasswd` ist in `.gitignore` und wird NICHT committet!
Siehe `deploy/nginx.htpasswd.example` für ein Beispiel-Format.

2. **In docker-compose.prod.yml mounten:**
```yaml
services:
  nginx:
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deploy/nginx.htpasswd:/etc/nginx/.htpasswd:ro
```

**Hinweis:** Das Volume-Mount ist bereits in `docker-compose.prod.yml` konfiguriert.
Für Development: Füge das Volume-Mount manuell in `docker-compose.yml` hinzu, falls benötigt.

3. **In nginx.conf aktivieren:**
```nginx
server {
    server_name control-plane.local;
    
    auth_basic "Control Plane - Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        # ... proxy config
    }
}
```

### Option 2: IP Allowlist (Empfohlen für interne Services)

```nginx
server {
    server_name control-plane.local;
    
    # Nur interne IPs erlauben
    allow 10.0.0.0/8;
    allow 172.16.0.0/12;
    allow 192.168.0.0/16;
    deny all;
    
    location / {
        # ... proxy config
    }
}
```

### Option 3: VPN-Only (Empfohlen für Production)

- Services nur über VPN erreichbar machen
- Keine öffentliche Exposition
- IP allowlist auf VPN-IP-Range beschränken

## Aktuelle Konfiguration

Die nginx.conf und nginx.tls.conf Dateien enthalten jetzt:
- Kommentierte Basic Auth Beispiele
- Kommentierte IP allowlist Beispiele
- Security-Warnungen in Kommentaren

**WICHTIG:** Vor Production müssen Basic Auth oder IP allowlist aktiviert werden!

## Services die geschützt werden müssen

1. **Control-Plane** (`control-plane.local`)
   - Admin-Key bereits vorhanden, aber nginx sollte zusätzlich schützen
   - Basic Auth oder IP allowlist

2. **Langfuse** (`langfuse.local`)
   - Observability UI
   - Basic Auth oder IP allowlist

3. **Grafana** (falls exponiert)
   - Metrics Dashboard
   - Basic Auth oder IP allowlist

## server_name Validierung

Die aktuelle Konfiguration nutzt:
- `server_name control-plane.local;` - nur für diesen Hostname
- `server_name _;` mit `default_server` - für alle anderen Requests

**Sicherheit:** `default_server` sollte auf Gateway zeigen (nicht auf Control-Plane/Langfuse).

## Testing

```bash
# Test ohne Auth (sollte 401 geben, wenn Basic Auth aktiviert)
curl -v http://control-plane.local/

# Test mit Auth
curl -v -u admin:password http://control-plane.local/

# Test IP allowlist (von externer IP sollte 403 geben)
curl -v http://control-plane.local/
```

