# DHL Tracking Skill

DHL Paketverfolgung via **DHL.de internationale Verfolgung** – ohne API-Key, ohne Registrierung.

## Features

- 🚫 **Kein API-Key nötig** – Nutzt öffentliche DHL.de Verfolgung
- 🌐 **International** – Funktioniert weltweit
- 📦 **Automatische Status-Erkennung**
- ⏰ **Überwachung um 10:00 und 16:00 Uhr**
- 📱 **JSON-Output für Weiterverarbeitung**

## Installation

```bash
cd ~/.openclaw/workspace/skills/dhl-tracking/
```

**Keine Abhängigkeiten nötig!** Nutzt nur Python-Standard-Library.

## Verwendung

```bash
# Paket tracken (20-stellige Nummer)
python3 scripts/dhl_tracker.py 00340434797565060012

# Nur bei relevantem Status
python3 scripts/dhl_tracker.py 00340434797565060012 --quiet

# JSON-Output
python3 scripts/dhl_tracker.py 00340434797565060012 --json
```

## API-Details

- **URL:** `https://www.dhl.de/int-verfolgen/data/search`
- **Parameter:**
  - `piececode`: Tracking-Nummer
  - `language`: Sprache (de, en, etc.)
- **Response:** JSON mit Sendungsdetails
- **Keine Authentifizierung nötig!**

## Sicherheit

- Keine Tracking-Daten werden gespeichert
- Nur aktueller Status wird abgefragt
- Keine Weitergabe an Dritte

---
*DHL Paketverfolgung für OpenClaw – Ohne API-Key!* 📦
