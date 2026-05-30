# Package Tracking Skill

**Einheitliches Paket-Tracking für DHL, Hermes, GLS und DPD**

Zentralisierte Verwaltung aller Pakete mit automatischem Tracking, Datenbank-Integration und Telegram-Benachrichtigungen.  
**Ein Skill – alle Carrier als Plugins.**

## Features

- 🏠 **Ein Skill, alle Carrier** — DHL + Hermes + GLS + DPD als Plugins
- 📦 **Zentrale DB** — SQLite für alle Pakete
- 🔄 **Automatisches Tracking** — 10:00 & 16:00 Uhr (Cron)
- 📱 **Telegram Updates** — Status-Änderungen in Topic 695
- 🧠 **Smart Status** — Normalisierte Status-Codes über alle Carrier
- 🛡️ **Retry-Logik** — Automatische Wiederholungen bei Fehlern
- 🔌 **Plugin-Architektur** — Jeder Carrier ist ein eigenes Python-Script

## Installation

```bash
# Für Hermes + DPD (Playwright/OCR)
pip install playwright pytesseract Pillow
playwright install chromium
apt-get install tesseract-ocr-deu

# Für DHL + GLS — KEINE Extras! (nur Python-Standard-Library)
```

## Schnellstart

### Paket hinzufügen
```bash
python3 scripts/package_manager.py add -c [CODE] -r dhl -d "Amazon Bestellung"
python3 scripts/package_manager.py add -c [CODE] -r hermes -d "Kleidung"
python3 scripts/package_manager.py add -c [CODE] -r gls -d "Paket aus NL"
python3 scripts/package_manager.py add -c [CODE] -r dpd -d "Möbel"
```

### Manuelles Tracking
```bash
python3 scripts/package_manager.py track
python3 scripts/package_manager.py track --json   # Maschinenlesbar
```

### Alle Pakete anzeigen
```bash
python3 scripts/package_manager.py list
python3 scripts/package_manager.py status          # JSON-Status
```

## Architektur (Plugin-System)

```
package_manager.py          ← Koordinator (Hauptscript)
    │
    ├─► dhl_tracker.py      ← DHL.de öffentlich + JSON (keine Extras)
    │
    ├─► hermes_tracker.py   ← Browser + OCR (Playwright + Tesseract)
    │
    ├─► gls_tracker.py      ← GLS REST-API (keine Extras, nur urllib)
    │
    └─► dpd_tracker.py      ← Browser (Playwright)
```

Das Hauptscript `package_manager.py` wählt anhand des `carrier`-Parameters automatisch das richtige Plugin aus.  
Neue Carrier werden einfach als weiteres Plugin-Script hinzugefügt und im Script-Verzeichnis abgelegt.

## Automatisches Tracking (Cron)

Läuft automatisch via Cron-Job:
- **10:00 Uhr** — Morgen-Check
- **16:00 Uhr** — Nachmittags-Check

Alle aktiven Pakete (DHL + Hermes + GLS + DPD) werden geprüft.  
Bei Status-Änderung: DB-Update + Telegram-Post in Topic 695.

## Datenbank-Schema

Tabelle: `packages`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| tracking_code | TEXT | Tracking-Nummer |
| carrier | TEXT | dhl / hermes / gls / dpd |
| status | TEXT | Aktueller Status (normalisiert) |
| delivered | INTEGER | 0 = unterwegs, 1 = zugestellt |
| delivered_at | TEXT | ISO-Timestamp der Zustellung |
| description | TEXT | Benutzer-Notiz |

## Carrier-Übersicht

| Carrier | Methode | Geschwindigkeit | Extras nötig |
|---------|---------|----------------|--------------|
| **DHL** | DHL.de (öffentl. JSON-Endpoint) | ⚡ Schnell (~5s) | ❌ Keine |
| **Hermes** | Browser + OCR (Screenshot) | 🐌 Langsam (~60s) | ✅ Playwright + Tesseract |
| **GLS** | GLS REST-API (gls-group.eu) | ⚡ Schnell (~2s) | ❌ Keine (nur urllib) |
| **DPD** | Browser (Playwright) | 🐢 Mittel (~30s) | ✅ Playwright |

**DHL + GLS** benötigen keine zusätzlichen Abhängigkeiten — nur Python-Standard-Library.  
**Hermes + DPD** benötigen Playwright (Browser-Automation). Hermes zusätzlich Tesseract OCR.

## Troubleshooting

### "Playwright nicht installiert"
```bash
pip install playwright
playwright install chromium
```

### "Tesseract OCR fehlgeschlagen" (nur Hermes)
```bash
apt-get install tesseract-ocr-deu
```

### GLS: "HTTP 500 / Ungültige Nummer"
Die GLS-API liefert 500 bei unbekannten/abgelaufenen Nummern. Das ist erwartet — kein Fehler im Script.

### Keine DHL-API-Daten
DHL hat Rate-Limiting. Retry-Logik aktiv (3 Versuche). Bei Dauerfehler: Manuell auf dhl.de prüfen.

## GitHub

https://github.com/James-Butler2026/openclaw-skills/tree/main/package-tracking

---
*Ein Skill für alle Pakete — mit Plugin-Architektur* 📦🎩
