# Calendar Skill

Lokaler Kalender mit natürlicher Spracheingabe und automatischen Erinnerungen.

## Features

- 📅 Natürliche Sprache: "Termin morgen 14 Uhr"
- 🎂 Geburtstage mit jährlichen Erinnerungen
- 🔔 Automatische Cron-Erinnerungen
- 🔄 Wiederholungen: täglich, wöchentlich, monatlich, jährlich
- 💾 SQLite-basiert, keine Cloud

## Installation

```bash
cd ~/.openclaw/workspace/skills/calendar/
```

## Verwendung

```bash
# Termin erstellen
python3 scripts/calendar_cli.py "Termin morgen 14 Uhr mit Arzt"

# Heutige Termine anzeigen
python3 scripts/calendar_cli.py --today

# Wöchentliche Übersicht
python3 scripts/calendar_cli.py --week

# Import aus Datei
python3 scripts/import_events.py events.csv
```

## Konfiguration

Keine API-Keys nötig – rein lokale SQLite-Datenbank.

## Sicherheit

- Alle Daten bleiben lokal in `~/.openclaw/workspace/data/`
- Keine Cloud-Synchronisation
- Datenschutzfreundlich

---
*Lokaler Kalender für OpenClaw* 📅
