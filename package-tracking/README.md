# Package Tracking Skill

**Einheitliches Paket-Tracking für Hermes, DHL, GLS (DPD in Planung)**

Zentralisierte Verwaltung aller Pakete mit automatischem Tracking, Datenbank-Integration und Telegram-Benachrichtigungen.

## Features

- 🏠 **Ein Skill, alle Carrier** - Hermes + DHL + GLS
- 📦 **Zentrale DB** - SQLite für alle Pakete
- 🔄 **Automatisches Tracking** - 10:00 & 16:00 Uhr
- 📱 **Telegram Updates** - Status-Änderungen in Topic 695
- 🧠 **Smart Status** - Normalisierte Status-Codes für alle Carrier
- 🛡️ **Retry-Logik** - Automatische Wiederholungen bei Fehlern
- 🚫 **Kein API-Key** - DHL und GLS nutzen öffentliche Endpunkte

## Carrier-Übersicht

| Carrier | Methode | API-Key | Abhängigkeiten | Geschwindigkeit | Status |
|---------|---------|---------|----------------|-----------------|--------|
| 🚚 DHL | REST API (öffentlich) | ❌ | Keine (stdlib) | ~2s | ✅ |
| 📦 Hermes | Browser + OCR | ❌ | Playwright, Tesseract | ~30s | ✅ |
| 🔵 GLS | REST API (öffentlich) | ❌ | Keine (stdlib) | ~2s | ✅ (NEU) |
| ⚪ DPD | offen | ❓ | offen | offen | ❓ Test ausstehend |

## Installation

### Für DHL und GLS (keine Extras)
```bash
# Keine zusätzlichen Abhängigkeiten nötig!
# Nutzen nur Python-Standardbibliothek
```

### Für Hermes (Browser + OCR)
```bash
pip install playwright pytesseract Pillow
playwright install chromium
apt-get install tesseract-ocr-deu
```

## Schnellstart

### Paket hinzufügen
```bash
# Hermes
python3 scripts/package_manager.py add -c [CODE] -r hermes -d "Beschreibung"

# DHL
python3 scripts/package_manager.py add -c [CODE] -r dhl -d "Amazon"

# GLS
python3 scripts/package_manager.py add -c [CODE] -r gls -d "Mein Paket"
```

### Manuelles Tracking (alle Carrier)
```bash
python3 scripts/package_manager.py track --json
```

### Alle Pakete anzeigen
```bash
python3 scripts/package_manager.py list
```

## Tracking-Nummern-Formate

| Carrier | Format | Beispiel |
|---------|--------|----------|
| DHL | 20 Ziffern / 12+ alphanumerisch | `00340434797565060012` |
| Hermes | H + 16+ Ziffern | `H1234567890123456` |
| GLS | 14 Ziffern (DE) / 11 Ziffern (IT) | `12345678901234` |

## Architektur

```
package-tracking/
├── SKILL.md                    ← Dokumentation
└── scripts/
    ├── package_manager.py       ← Hauptscript (Koordinator, DB)
    ├── dhl_tracker.py           ← DHL.de öffentlich + JSON
    ├── hermes_tracker.py        ← Browser + OCR
    ├── gls_tracker.py           ← GLS REST API (öffentlich)
    └── package_tracking_agent.py ← OpenClaw Agent
```

## Automatisches Tracking (Cron)

Der Skill läuft automatisch über Cron:
- **10:00 Uhr** - Morgen-Check
- **16:00 Uhr** - Nachmittags-Check

Alle aktiven Pakete (DHL + Hermes + GLS) werden geprüft. Bei Status-Änderung:
1. DB wird aktualisiert
2. Telegram-Post in Topic 695
3. Bei Zustellung: `delivered_at` gespeichert

## Status-Codes (alle Carrier)

| Code | Bedeutung |
|------|-----------|
| `delivered` | ✅ Zugestellt |
| `in_delivery` | 🚚 Im Zustellfahrzeug |
| `in_transit` | 📦 Unterwegs |
| `picked_up` | 📤 Abgeholt |
| `in_store` | 🏪 In Filiale |
| `announced` | 📋 Elektronisch angekündigt |
| `exception` | ⚠️ Problem/Verzögerung |

## GitHub

https://github.com/James-Butler2026/openclaw-skills/tree/main/package-tracking

---
*Ein Skill für alle Pakete* 📦🎩
