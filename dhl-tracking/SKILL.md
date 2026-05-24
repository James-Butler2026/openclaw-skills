---
name: dhl-tracking
description: DHL Paketverfolgung via DHL.de internationale Verfolgung. Überwacht Sendungen automatisch ohne API-Key.
---

# DHL Sendungsverfolgung

Automatisierte DHL-Paketverfolgung via öffentlicher DHL.de internationaler Verfolgung. **Kein API-Key nötig!**

## Features

- 🚫 **Kein API-Key** – Nutzt öffentliche DHL.de Verfolgung
- 🌐 **International** – Funktioniert weltweit
- 📦 **Automatische Überwachung** – Erkennt Status-Änderungen
- 📱 **Telegram-Benachrichtigung** – Bei Zustellung oder wichtigen Updates
- 📊 **JSON-Output** – Für Weiterverarbeitung

## Überwachte Status

| Status | Bedeutung |
|--------|-----------|
| "Die Sendung wurde elektronisch angekündigt" | 📦 Elektronisch angekündigt |
| "in das Zustellfahrzeug geladen" | 🚚 Heute Zustellung |
| "Zustellung erfolgreich" | ✅ Paket angekommen |
| "Briefzentrum bearbeitet" | 📦 In Bearbeitung |

## Installation

### Abhängigkeiten

```bash
# Keine externen Abhängigkeiten nötig!
# Nutzt nur Python-Standard-Library (urllib, json)
```

## Nutzung

### Einzelnes Paket tracken

```bash
# Standard-Output
python3 scripts/dhl_tracker.py 00340434797565060012

# JSON-Output
python3 scripts/dhl_tracker.py 00340434797565060012 --json

# Nur Ergebnisse (kein Header)
python3 scripts/dhl_tracker.py 00340434797565060012 --quiet
```

### Beispiel-Output

```
============================================================
🚚 DHL SENDUNGSSTATUS
📦 00340434797565060012
============================================================

✅ Status: Die Sendung wurde elektronisch angekündigt.
📊 Fortschritt: 1/5

📋 Letzte Updates:
   • 2026-04-29T20:50: Die Sendung wurde elektronisch angekündigt. Sobald...
============================================================
```

### Automatische Überwachung

Füge zu den Cron-Jobs hinzu:

```bash
# 10:00 Uhr: Morgendlicher Check
# 16:00 Uhr: Nachmittags-Check
```

Oder nutze den Package Manager für zentrale Verwaltung:

```bash
# Paket hinzufügen
python3 skills/hermes-tracking/scripts/package_manager.py add \
    --code 00340434797565060012 \
    --carrier dhl \
    --desc "Whey Protein Amazon"

# Alle Pakete tracken
python3 skills/hermes-tracking/scripts/package_manager.py track --json
```

## API-Details

- **URL:** `https://www.dhl.de/int-verfolgen/data/search`
- **Parameter:**
  - `piececode`: Tracking-Nummer
  - `language`: Sprache (de, en, etc.)
- **Response:** JSON mit Sendungsdetails, Status, Events
- **Keine Authentifizierung nötig!**

## Hinweise

- Tracking-Nummern: Exakt 20 Ziffern
- Keine Rate-Limits bekannt
- Sprache: Deutsch (language=de)
- Ziel-Land: Wird automatisch erkannt

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Keine Sendungsdaten gefunden" | Tracking-Nummer prüfen |
| "HTTP Fehler 404" | DHL Server temporär nicht erreichbar |
| "Timeout" | Erneut versuchen |

## Unterschied zur alten API-Version

| Feature | Alt (API) | Neu (DHL.de) |
|---------|-----------|--------------|
| API-Key | ❌ Nötig | ✅ Nicht nötig |
| requests-Lib | ❌ Nötig | ✅ Nicht nötig |
| logger_config | ❌ Nötig | ✅ Nicht nötig |
| Zuverlässigkeit | ⚠️ API kann sich ändern | ✅ Öffentliche URL |
| International | ⚠️ Eingeschränkt | ✅ Vollständig |

## Lizenz

MIT License – Open Source, frei nutzbar.

---

**Wichtig:** Dieser Skill nutzt die öffentliche DHL.de internationale Verfolgung. Keine offizielle DHL API-Integration.
