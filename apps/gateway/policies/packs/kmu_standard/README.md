# KMU Standard Policy Pack

**Version:** 1.0.0  
**Zielgruppe:** Kleine und mittlere Unternehmen

## Beschreibung

Diese Policy bietet einen ausgewogenen Schutz für KMU-Anwendungen mit moderaten Sicherheitsanforderungen. Sie balanciert Sicherheit und Benutzerfreundlichkeit.

## Features

- **PII-Schutz:** E-Mails und Telefonnummern werden maskiert, Kreditkartennummern blockiert
- **Prompt-Injection-Schutz:** Moderate Erkennung mit Threshold 6
- **Tool-Permissions:** Risky Tools erfordern Approval
- **Compatibility Mode:** Standardmäßig "warn" (nicht-blockierend)

## Verwendung

```yaml
# In metadata setzen:
metadata:
  ai_shield_preset: kmu_standard
  compatibility_mode: warn  # oder: observe, block
```

## Konfiguration

Die Policy kann über `policy.yaml` angepasst werden. Änderungen erfordern einen Neustart des Gateways.

## Changelog

### 1.0.0 (2025-01-XX)
- Initiale Version
- PII-Maskierung für E-Mail und Telefon
- Kreditkarten-Blockierung
- Prompt-Injection-Schutz

