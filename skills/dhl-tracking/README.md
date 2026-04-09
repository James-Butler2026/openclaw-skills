# dhl-tracking

---
name: dhl-tracking
description: DHL Paketverfolgung via REST API. Überwacht Sendungen automatisch.
---

# DHL Sendungsverfolgung

Automatisierte DHL-Paketverfolgung via offizieller API.

## Features

- Direkte API-Abfrage – Kein Browser nötig
- Überwachte Status – Erkennt wichtige Zustell-Events
- Automatische Checks – 10:00 und 16:00 Uhr
- JSON-Output – Für Weiterverarbeitung

## Überwachte Status

| Status | Bedeutung |
|--------|-----------|
| "in das Zustellfahrzeug geladen" | 🚚 Heute Zustellung |
| "Zustellung erfolgreich" | ✅ Paket angekommen |
| "Briefzentrum bearbeitet" | 📦 In Bearbeitung |

## Installation

### Abhängigkeiten

```bash
pip install requests
```

## Nutzung

### Direkt

```bash
# Einzelnes Paket tracken
python3 scripts/dhl_tracker.py 00340434886241560288

# Nur bei relevantem Status ausgeben (für Cron)
python3 scripts/dhl_tracker.py 00340434886241560288 --quiet

# JSON-Output
python3 scripts/dhl_tracker.py 00340434886241560288 --json
```

## Automatische Überwachung

Füge zu den Cron-Jobs hinzu:
- 10:00 Uhr: Check auf "in Zustellfahrzeug geladen"
- 16:00 Uhr: Check auf Zustellstatus

## Hinweise

- Tracking-Nummern: Exakt 20 Ziffern
- API: DHL interner Endpoint (keine Auth nötig)
- Sprache: Deutsch (language=de)
