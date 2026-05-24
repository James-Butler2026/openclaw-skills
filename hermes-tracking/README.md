# Hermes Tracking Skill

Hermes Paketverfolgung mit Browser-Automation und OCR.

## Features

- 🌐 Playwright + Chromium Browser
- 🔍 OCR-Textextraktion mit Tesseract
- 📸 Screenshot-Archivierung
- ⏰ Automatische Cron-Verwaltung

## Installation

```bash
cd ~/.openclaw/workspace/skills/hermes-tracking/

# Playwright installieren (falls nötig)
# playright install chromium
```

## Verwendung

```bash
# Paket tracken
python3 scripts/hermes_tracker.py [DEINE_TRACKING_NUMMER]

# Mit sichtbarem Browser (Debug)
python3 scripts/hermes_tracker.py [DEINE_TRACKING_NUMMER] --show-browser
```

## Konfiguration

Keine zusätzliche Konfiguration nötig.

## Sicherheit

- Tracking-Nummern werden nicht gespeichert
- Screenshots nur lokal
- Keine Weitergabe an Dritte

---
*Hermes Paketverfolgung für OpenClaw* 📦
