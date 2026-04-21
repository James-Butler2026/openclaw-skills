# Hermes Sendungsverfolgung

Automatisierte Hermes-Paketverfolgung mit Browser-Automation, Screenshot und OCR.

## Features

- **Browser-Automation** via Playwright (Chromium)
- **OCR-Textextraktion** mit Tesseract
- **Status-Erkennung** für wichtige Zustell-Events
- **Screenshot-Archivierung** für Nachweis/Nachvollziehbarkeit
- **Automatische Cron-Verwaltung** – Cron wird bei Zustellung automatisch gelöscht
- **Gemeinsame Datenbank** – Nutzt dieselbe SQLite-DB wie der DHL-Skill

## Status-Erkennung

Der Tracker erkennt folgende Status-Meldungen:

| Status | Bedeutung |
|--------|-----------|
| "Die Sendung wurde an der Empfangsadresse zugestellt" | ✅ Paket zugestellt |
| "Die Sendung wurde ins Zustellfahrzeug geladen" | 🚚 Unterwegs (heute) |
| "Die Sendung liegt in der Filiale bereit" | 🏪 Abholbereit |
| "Die Sendung wurde vom Absender an Hermes übergeben" | 📤 Versendet |

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/James-Butler2026/openclaw-skills.git
cd openclaw-skills/hermes-tracking
```

### 2. System-Abhängigkeiten installieren

```bash
# Ubuntu/Debian (im Docker ohne sudo)
apt-get update
apt-get install tesseract-ocr tesseract-ocr-deu

# Tesseract überprüfen
tesseract --version
tesseract --list-langs  # Sollte 'deu' enthalten
```

### 3. Python-Abhängigkeiten installieren

```bash
pip install playwright pytesseract Pillow
playwright install chromium
```

### 4. Playwright überprüfen

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Automatisches Tracking-Setup

Eure Lordschaft gibt mir die Tracking-Nummer – ich erledige den Rest:

### Workflow:

1. **Paket hinzufügen:**
   ```bash
   python3 scripts/package_manager.py add -c H1003660401590901036 -r hermes -d "Amazon Bestellung"
   ```

2. **Automatische Einrichtung:**
   - Speichert in SQLite-Datenbank (`data/james.db`)
   - Erstellt Cron-Jobs für 10:00 und 16:00 Uhr
   - Überwacht Status automatisch

3. **Bei Zustellung:**
   - Cron-Job wird automatisch gelöscht
   - Paket als "geliefert" markiert
   - Keine weiteren Checks nötig

## Nutzung

### Direkt

```bash
# Mit Tracking-Code
python3 scripts/hermes_tracker.py H1003660401590901036

# Mit voller URL
python3 scripts/hermes_tracker.py "https://www.myhermes.de/...#H1003660401590901036"

# Mit sichtbarem Browser (für Debugging)
python3 scripts/hermes_tracker.py H1003660401590901036 --show-browser
```

## Hinweise

- **Headless-Modus**: Standardmäßig unsichtbar (schneller)
- **Timeout**: 30 Sekunden für Seitenladezeit
- **OCR**: Deutsche Sprache (deu) für optimale Erkennung

## Troubleshooting

### "Playwright nicht installiert"
```bash
pip install playwright
playwright install chromium
```

### "OCR fehlgeschlagen"
```bash
# Tesseract installiert?
which tesseract

# Deutsche Sprachdaten?
tesseract --list-langs  # Sollte 'deu' enthalten

# Nachinstallation (im Docker ohne sudo):
apt-get install tesseract-ocr-deu
```

### Seite lädt nicht
- `--show-browser` verwenden um zu sehen was passiert
- Internetverbindung prüfen
- Tracking-Code auf Gültigkeit prüfen
