# Deployment Guide - Branchen-Pakete

Dieser Guide beschreibt den Production-Rollout der Branchen-Pakete.

---

## 🚀 Pre-Deployment Checklist

### 1. Production Readiness Check

```bash
# Prüfe Production-Readiness
python apps/agents/scripts/check_production_ready.py
```

**Erwartetes Ergebnis:**
- ✅ Alle Checks PASS
- ⚠️  Warnings sind OK (z.B. Mock-Integrationen)
- ❌ FAILs müssen behoben werden

### 2. Tests ausführen

```bash
# Alle Tests
python apps/agents/scripts/run_tests.py

# Oder direkt mit pytest
pytest apps/agents/tests/ -v
```

**Erwartetes Ergebnis:**
- Alle Tests bestehen
- Keine kritischen Fehler

### 3. Integration prüfen

```bash
# Integration Layer verbinden
python apps/agents/scripts/connect_integrations.py
```

**Wichtig:**
- Echte Integrationen müssen eingebunden werden
- Mock-Integrationen nur für Testing

---

## 📦 Deployment Steps

### Phase 1: Staging

1. **Package Manifest erstellen**
   ```python
   from apps.agents.shared.vertical_package_manifest import (
       VerticalPackageManifest, PackageType, get_registry
   )
   
   manifest = VerticalPackageManifest(
       package_type=PackageType.GASTRONOMY,
       account_id="staging-restaurant-1",
       enabled_agents=["gastronomy_supervisor_agent", "restaurant_voice_host_agent"]
   )
   
   registry = get_registry()
   registry.save_manifest(manifest)
   ```

2. **Monitoring aktivieren**
   ```python
   from apps.agents.core.monitoring import get_monitor
   
   monitor = get_monitor()
   # Monitoring läuft automatisch
   ```

3. **Integration Layer verbinden**
   ```python
   from apps.agents.core.integration_layer import connect_to_existing_system
   
   connect_to_existing_system(
       communications_supervisor=real_communications_supervisor,
       integration_agent=real_integration_agent
   )
   ```

4. **Test-Requests senden**
   ```python
   from apps.agents.core.global_orchestrator_agent import get_orchestrator, RoutingRequest
   
   orchestrator = get_orchestrator()
   request = RoutingRequest(
       account_id="staging-restaurant-1",
       user_message="Ich möchte einen Tisch reservieren",
       channel="phone"
   )
   
   response = orchestrator.route(request)
   ```

### Phase 2: Canary Deployment

1. **Einzelne Accounts aktivieren**
   - Starte mit 1-2 Test-Accounts
   - Monitor Metrics genau
   - Prüfe Error-Rate

2. **Graduelle Erweiterung**
   - Erhöhe auf 10% der Accounts
   - Dann 25%, 50%, 100%

### Phase 3: Full Production

1. **Alle Accounts aktivieren**
2. **Monitoring verstärken**
3. **Alerting einrichten**

---

## 📊 Monitoring Setup

### Prometheus Metrics

```bash
# Metrics exportieren
python apps/agents/scripts/export_metrics.py
```

**Wichtige Metrics:**
- `agent_requests_total` - Request-Rate
- `agent_errors_total` - Error-Rate
- `agent_handoffs_total` - Handoff-Rate
- `agent_consent_checks_total` - Consent-Checks

### Grafana Dashboard

Erstelle Dashboard mit:
- Request-Rate pro Agent
- Error-Rate
- Routing-Entscheidungen
- Handoff-Rate
- Performance (Duration)

### Alerting Rules

```yaml
# Beispiel Prometheus Alert
groups:
  - name: agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(agent_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Hohe Error-Rate bei Agents"
      
      - alert: HighHandoffRate
        expr: rate(agent_handoffs_total[5m]) > 0.2
        for: 5m
        annotations:
          summary: "Viele Handoffs - mögliches Problem"
```

---

## 🔍 Post-Deployment Monitoring

### Wichtige KPIs

1. **Request-Rate**
   - Pro Agent
   - Pro Account
   - Pro Package Type

2. **Error-Rate**
   - Sollte < 1% sein
   - Kritische Errors sofort alerten

3. **Performance**
   - Average Response Time
   - P95, P99 Latency

4. **Handoff-Rate**
   - Sollte < 5% sein
   - Bei Anstieg: Problem analysieren

5. **Consent-Checks**
   - Grant-Rate
   - Compliance

### Logging

```python
import logging

# Agent-Logging
logger = logging.getLogger("apps.agents")
logger.info("Agent action", extra={
    "account_id": account_id,
    "agent": agent_name,
    "action": action
})
```

**Wichtige Log-Levels:**
- INFO: Normale Operationen
- WARNING: Wichtige Events (Handoffs, etc.)
- ERROR: Fehler
- CRITICAL: Kritische Fehler

---

## 🐛 Troubleshooting

### Problem: Agent nicht gefunden

```python
# Prüfe Registry
from apps.agents.core.agent_registry import get_registry
registry = get_registry()
print(registry.list_agents())

# Prüfe Manifest
from apps.agents.shared.vertical_package_manifest import get_registry
manifest_registry = get_registry()
manifest = manifest_registry.get_manifest(account_id)
print(manifest.enabled_agents)
```

### Problem: Hohe Error-Rate

1. **Logs prüfen**
2. **Metrics analysieren**
3. **Integrationen testen**
4. **Rollback erwägen**

### Problem: Performance-Issues

1. **Request-Times analysieren**
2. **Bottlenecks identifizieren**
3. **Caching prüfen**
4. **Optimierungen**

---

## 🔄 Rollback Plan

### Schneller Rollback

1. **Package Manifest deaktivieren**
   ```python
   manifest.enabled_agents = []  # Alle deaktivieren
   registry.save_manifest(manifest)
   ```

2. **Fallback-Routing aktivieren**
   - Global Orchestrator nutzt Fallback

3. **Monitoring weiterlaufen lassen**
   - Für Analyse

---

## ✅ Success Criteria

- ✅ Error-Rate < 1%
- ✅ Average Response Time < 2s
- ✅ Handoff-Rate < 5%
- ✅ Alle Tests bestehen
- ✅ Monitoring aktiv
- ✅ Alerts konfiguriert

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2024
