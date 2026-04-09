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
| "Die Sendung wurde ins Zustellfahrzeug geladen und wird voraussichtlich heute zugestellt" | 🚚 Unterwegs (heute) |
| "Die Sendung wurde im Paketshop abgeholt" | 📦 Abgeholt |
| "Die Sendung liegt in der Filiale bereit zur Abholung" | 🏪 Abholbereit |
| "Die Sendung wurde vom Absender an Hermes übergeben" | 📤 Versendet |

## Installation

### Voraussetzungen

Tesseract und Playwright müssen auf Systemebene installiert sein (Docker-Image bereits vorkonfiguriert):

```bash
# System-Pakete (im Docker-Image bereits vorhanden)
# tesseract-ocr tesseract-ocr-deu

# Python-Pakete installieren
pip install playwright pytesseract Pillow
playwright install chromium
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

### Datenbank-Schema (gemeinsam mit DHL):

```sql
CREATE TABLE packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_code TEXT NOT NULL UNIQUE,
    carrier TEXT NOT NULL,  -- 'hermes' oder 'dhl'
    description TEXT,
    status TEXT,
    active BOOLEAN DEFAULT 1,  -- 0 wenn zugestellt
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Nutzung

### Direkt

```bash
# Mit Tracking-Code
python3 scripts/hermes_tracker.py H1003660401590901036

# Mit voller URL
python3 scripts/hermes_tracker.py "https://www.myhermes.de/empfangen/sendungsverfolgung/sendungsinformation#H1003660401590901036"

# Mit sichtbarem Browser (für Debugging)
python3 scripts/hermes_tracker.py H1003660401590901036 --show-browser

# Screenshot an benutzerdefiniertem Ort
python3 scripts/hermes_tracker.py H1003660401590901036 -o ~/tracking/paket_123.png
```

### Python-Modul

```python
from scripts.hermes_tracker import extract_tracking_code

# Tracking-Code aus URL extrahieren
code = extract_tracking_code("https://...#H1003660401590901036")
# -> H1003660401590901036
```

## Ausgabe

Das Skript gibt:
- ✅ Erkannten Status (sofern gefunden)
- 📦 Tracking-Nummer
- 🕐 Zeitstempel
- 📅 Gefundene Daten im Text
- 📁 Pfad zum Screenshot

## Screenshot-Speicherort

Standard: `/tmp/hermes_{TRACKINGCODE}_{ZEITSTEMPEL}.png`

Beispiel: `/tmp/hermes_H1003660401590901036_20250324_114530.png`

## Hinweise

- **Headless-Modus**: Standardmäßig unsichtbar (schneller)
- **Timeout**: 30 Sekunden für Seitenladezeit
- **Cookie-Banner**: Wird automatisch akzeptiert (falls erkannt)
- **OCR**: Deutsche Sprache (deu) für optimale Erkennung

## Troubleshooting

### "Playwright nicht installiert"
```bash
pip install playwright
playwright install chromium
```

### "OCR fehlgeschlagen"
- Tesseract installiert? `which tesseract`
- Deutsche Sprachdaten? `tesseract --list-langs` (sollte `deu` enthalten)

### Seite lädt nicht
- `--show-browser` verwenden um zu sehen was passiert
- Internetverbindung prüfen
- Tracking-Code auf Gültigkeit prüfen
