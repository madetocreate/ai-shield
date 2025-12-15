# Scripts - Branchen-Pakete

Utility-Scripts für Testing, Monitoring und Deployment.

---

## 🧪 run_tests.py

Führt alle Agent-Tests aus.

```bash
python apps/agents/scripts/run_tests.py
```

**Output:**
- Detaillierte Test-Ergebnisse
- Exit Code 0 bei Erfolg, 1 bei Fehlern

---

## ✅ check_production_ready.py

Prüft Production-Readiness.

```bash
python apps/agents/scripts/check_production_ready.py
```

**Prüft:**
- ✅ Imports
- ✅ Shared Components
- ✅ Agent-Registry
- ✅ Integrationen
- ✅ Monitoring
- ✅ Konfiguration

**Output:**
- Detaillierter Report
- Exit Code 0 wenn ready, 1 wenn nicht

---

## 📊 export_metrics.py

Exportiert Metrics im Prometheus-Format.

```bash
python apps/agents/scripts/export_metrics.py
```

**Output:**
- Prometheus-Format Metrics
- Kann direkt von Prometheus gescraped werden

**Integration:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'agents'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## 🔌 connect_integrations.py

Verbindet Integration Layer mit bestehendem System.

```bash
python apps/agents/scripts/connect_integrations.py
```

**Wichtig:**
- Script muss angepasst werden mit echten Integrationen
- Aktuell werden Mock-Integrationen verwendet

**Beispiel-Anpassung:**
```python
from your_system import CommunicationsSupervisor, IntegrationAgent

connect_to_existing_system(
    communications_supervisor=CommunicationsSupervisor(),
    integration_agent=IntegrationAgent()
)
```

---

## 📝 Verwendung

### Pre-Deployment

```bash
# 1. Production-Readiness prüfen
python apps/agents/scripts/check_production_ready.py

# 2. Tests ausführen
python apps/agents/scripts/run_tests.py

# 3. Integrationen verbinden
python apps/agents/scripts/connect_integrations.py
```

### Monitoring

```bash
# Metrics exportieren
python apps/agents/scripts/export_metrics.py > /tmp/agent_metrics.txt

# Oder als Service laufen lassen
while true; do
    python apps/agents/scripts/export_metrics.py
    sleep 30
done
```

---

## 🔧 Integration in CI/CD

### GitHub Actions Beispiel

```yaml
name: Agent Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run Tests
        run: python apps/agents/scripts/run_tests.py
      - name: Check Production Ready
        run: python apps/agents/scripts/check_production_ready.py
```

---

**Version:** 1.0.0
