# DHL Tracking Skill

Automatisierte DHL-Paketverfolgung via offizieller REST API.

## Features

- 🔌 Direkte API-Abfrage – Kein Browser nötig
- ✅ Überwachte Status-Erkennung
- 🕐 Automatische Checks um 10:00 und 16:00 Uhr
- 📊 JSON-Output für Weiterverarbeitung

## Schnellstart

```bash
# Einzelnes Paket tracken
python3 scripts/dhl_tracker.py 00340434886241560288

# Nur bei relevantem Status ausgeben (für Cron)
python3 scripts/dhl_tracker.py 00340434886241560288 --quiet

# JSON-Output
python3 scripts/dhl_tracker.py 00340434886241560288 --json
```

## Überwachte Status

| Status | Bedeutung |
|--------|-----------|
| "in das Zustellfahrzeug geladen" | 🚚 Heute Zustellung |
| "Zustellung erfolgreich" | ✅ Paket angekommen |
| "Briefzentrum bearbeitet" | 📦 In Bearbeitung |

## Konfiguration

Keine API-Keys nötig – DHL API ist öffentlich verfügbar!

## Hinweise

- Tracking-Nummern: Exakt 20 Ziffern
- API: DHL interner Endpoint (keine Auth nötig)
- Sprache: Deutsch (language=de)

---

*Teil der OpenClaw Skills Collection* 🎩
