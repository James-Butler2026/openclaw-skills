# Hermes Tracking Skill

Automatisierte Hermes-Paketverfolgung mit Browser-Automation.

## Features

- 🎭 Browser-Automation via Playwright (Chromium)
- 🔍 OCR-Textextraktion mit Tesseract
- ✅ Status-Erkennung für wichtige Zustell-Events
- 📸 Screenshot-Archivierung für Nachweis
- 🔄 Automatische Cron-Verwaltung

## Schnellstart

```bash
# Mit Tracking-Code
python3 scripts/hermes_tracker.py H1003660401590901036

# Mit voller URL
python3 scripts/hermes_tracker.py "https://www.myhermes.de/...#H1003660401590901036"

# Mit sichtbarem Browser (Debugging)
python3 scripts/hermes_tracker.py H1003660401590901036 --show-browser
```

## Status-Erkennung

| Status | Bedeutung |
|--------|-----------|
| "an der Empfangsadresse zugestellt" | ✅ Paket zugestellt |
| "ins Zustellfahrzeug geladen" | 🚚 Unterwegs (heute) |
| "in der Filiale bereit" | 🏪 Abholbereit |
| "vom Absender übergeben" | 📤 Versendet |

## Konfiguration

### System-Abhängigkeiten

```bash
# Ubuntu/Debian
apt-get update
apt-get install tesseract-ocr tesseract-ocr-deu

# Python-Abhängigkeiten
pip install playwright pytesseract Pillow
playwright install chromium
```

### Automatisches Tracking

```bash
# Paket hinzufügen
python3 scripts/package_manager.py add \
    -c H1003660401590901036 \
    -r hermes \
    -d "Amazon Bestellung"
```

- Speichert in SQLite-Datenbank (`data/james.db`)
- Erstellt Cron-Jobs für 10:00 und 16:00 Uhr
- Cron wird bei Zustellung automatisch gelöscht

---

*Teil der OpenClaw Skills Collection* 🎩
