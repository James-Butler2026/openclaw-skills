# DHL Tracking Skill

DHL Paketverfolgung via REST API – direkt und zuverlässig.

## Features

- 📦 Direkte API-Abfrage (kein Browser nötig)
- 🔔 Automatische Status-Erkennung
- ⏰ Überwachung um 10:00 und 16:00 Uhr
- 📱 JSON-Output für Weiterverarbeitung

## Installation

```bash
cd ~/.openclaw/workspace/skills/dhl-tracking/
```

## Verwendung

```bash
# Paket tracken (20-stellige Nummer)
python3 scripts/dhl_tracker.py 00340434886241560288

# Nur bei relevantem Status
python3 scripts/dhl_tracker.py 00340434886241560288 --quiet

# JSON-Output
python3 scripts/dhl_tracker.py 00340434886241560288 --json
```

## Konfiguration

Keine API-Key nötig – DHL REST API ist öffentlich.

## Sicherheit

- Keine Tracking-Daten werden gespeichert
- Nur aktueller Status wird abgefragt
- Keine Weitergabe an Dritte

---
*DHL Paketverfolgung für OpenClaw* 📦
