# Package Tracking Skill

**Einheitliches Paket-Tracking für Hermes und DHL**

Zentralisierte Verwaltung aller Pakete mit automatischem Tracking, Datenbank-Integration und Telegram-Benachrichtigungen.

## Features

- 🏠 **Ein Skill, alle Carrier** - Hermes + DHL zusammen
- 📦 **Zentrale DB** - SQLite für alle Pakete
- 🔄 **Automatisches Tracking** - 10:00 & 16:00 Uhr
- 📱 **Telegram Updates** - Status-Änderungen in Topic 695
- 🧠 **Smart Status** - Normalisierte Status-Codes
- 🛡️ **Retry-Logik** - Automatische Wiederholungen bei Fehlern

## Installation

```bash
# Dependencies installieren
pip install playwright requests pytesseract Pillow
playwright install chromium

# Für OCR (Deutsch)
apt-get install tesseract-ocr-deu
```

## Schnellstart

### Paket hinzufügen
```bash
python3 scripts/package_manager.py add -c [CODE] -r hermes -d "Beschreibung"
python3 scripts/package_manager.py add -c [CODE] -r dhl -d "Amazon"
```

### Manuelles Tracking
```bash
python3 scripts/package_manager.py track --json
```

### Alle Pakete anzeigen
```bash
python3 scripts/package_manager.py list
```

## Architektur

```
package_manager.py      ← Hauptscript (Koordinator)
    │
    ├─► hermes_tracker.py   ← Browser + OCR
    │
    └─► dhl_tracker.py      ← API + JSON
```

## Automatisches Tracking (Cron)

Der Skill läuft automatisch über Cron:
- **10:00 Uhr** - Morgen-Check
- **16:00 Uhr** - Nachmittags-Check

Alle aktiven Pakete werden geprüft. Bei Status-Änderung:
1. DB wird aktualisiert
2. Telegram-Post in Topic 695
3. Bei Zustellung: `delivered_at` gespeichert

## Datenbank-Schema

Tabelle: `packages`
| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| tracking_code | TEXT | Tracking-Nummer |
| carrier | TEXT | hermes / dhl |
| status | TEXT | aktueller Status |
| delivered | INTEGER | 0/1 |
| delivered_at | TEXT | ISO-Timestamp |
| description | TEXT | Benutzer-Notiz |

## Troubleshooting

### "Playwright nicht installiert"
```bash
pip install playwright
playwright install chromium
```

### "Tesseract OCR fehlgeschlagen"
```bash
apt-get install tesseract-ocr-deu
```

### Keine API-Daten (DHL)
- DHL hat Rate-Limiting
- Retry-Logik aktiv (3 Versuche)
- Bei Dauerfehler: Manuell prüfen

## Carrier-Unterstützung

| Carrier | Methode | Geschwindigkeit | Zuverlässigkeit |
|---------|---------|-----------------|-----------------|
| Hermes | Browser + OCR | Langsam (30-60s) | Sehr hoch |
| DHL | DHL.de öffentlich | Schnell (5-10s) | Hoch |

**Wichtig:** DHL nutzt die öffentliche internationale Verfolgung (dhl.de/int-verfolgen). Kein API-Key nötig!

## GitHub

https://github.com/James-Butler2026/openclaw-skills/tree/main/package-tracking

---
*Ein Skill für alle Pakete* 📦🎩
