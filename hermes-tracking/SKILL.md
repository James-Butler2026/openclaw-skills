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
   python3 scripts/package_manager.py add -c [DEINE_TRACKING_NUMMER] -r hermes -d "Beschreibung"
   ```

2. **Automatische Einrichtung:**
   - Speichert in SQLite-Datenbank (`data/james.db`, Tabelle `packages`)
   - Erstellt **dynamischen Cron-Job** (10:00 & 16:00 Uhr)
   - Überwacht **alle aktiven Pakete** automatisch
   - Postet Updates in **Telegram Topic 695**

3. **Bei Zustellung:**
   - Status automatisch auf `delivered` gesetzt
   - `delivered_at` mit aktuellem Datum/Zeit gefüllt
   - Zustellungs-Bestätigung in Topic 695
   - Cron bleibt aktiv für neue Pakete

## Datenbank-Schema (Tabelle: packages)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | INTEGER | Primärschlüssel |
| tracking_code | TEXT | Tracking-Nummer |
| carrier | TEXT | hermes / dhl |
| status | TEXT | aktueller Status |
| delivered | INTEGER | 0=nein, 1=ja |
| **delivered_at** | TEXT | **Zustelldatum (neu!)** |
| added_at | TIMESTAMP | Hinzugefügt am |
| updated_at | TIMESTAMP | Letzte Änderung |

## Automatisches Tracking (Empfohlen)

Der Cron-Job überwacht alle aktiven Pakete automatisch:
- ⏰ **10:00 & 16:00 Uhr** täglich
- 📍 **Telegram Topic 695** für Updates
- 🚚 Status-Änderungen werden automatisch gepostet
- ✅ Zustellung = Bestätigung + DB-Update

### Manuelles Tracking

```bash
# Einzelnes Paket prüfen
python3 scripts/hermes_tracker.py [TRACKING_NUMMER]

# Mit voller URL
python3 scripts/hermes_tracker.py "https://www.myhermes.de/...#[TRACKING_NUMMER]"

# Mit sichtbarem Browser (für Debugging)
python3 scripts/hermes_tracker.py [TRACKING_NUMMER] --show-browser
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
