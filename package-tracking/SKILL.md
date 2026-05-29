# Package Tracking

Einheitliches Paket-Tracking für DHL, Hermes, GLS und zukünftig DPD.
**Alle Carrier in einem Skill vereint.**

## Features

- 🔄 **Multi-Carrier** – DHL + Hermes + GLS aus einer Hand
- 🚫 **Kein API-Key** – Alle Carrier nutzen öffentliche Endpunkte
- 📦 **Automatische Überwachung** – Erkennt Status-Änderungen per Cron
- 📱 **Telegram-Benachrichtigung** – Updates bei Status-Änderungen
- 📊 **JSON-Output** – Zur Weiterverarbeitung
- 💾 **SQLite-Datenbank** – Tracking-Verlauf und Paketverwaltung

## Carrier-Übersicht

| Carrier | Methode | Abhängigkeiten | Geschwindigkeit | Status |
|---------|---------|----------------|-----------------|--------|
| 🚚 DHL | REST API (öffentlich) | Keine (nur stdlib) | ~2s | ✅ Fertig |
| 📦 Hermes | Browser + OCR | Playwright, Tesseract, Pillow | ~30s | ✅ Fertig |
| 🔵 GLS | REST API (öffentlich) | Keine (nur stdlib) | ~2s | ✅ Fertig (NEU!) |
| ⚪ DPD | *offen* | *offen* | *offen* | ❓ Test ausstehend |

## Installation

### Abhängigkeiten

Reading package lists...
Building dependency tree...
Reading state information...
tesseract-ocr is already the newest version (5.3.0-2).
tesseract-ocr-deu is already the newest version (1:4.1.0-2).
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.

## Nutzung

### Paket hinzufügen und verwalten

ℹ️  Paket bereits vorhanden oder Fehler
ℹ️  Paket bereits vorhanden oder Fehler
📦 Aktive Pakete: 6
============================================================
1. HERMES: [CODE]
   Status: registered
   Beschreibung: Beschreibung
   Letztes Update: 2026-05-29 08:27:17

2. GLS: 30027797654
   Status: registered
   Beschreibung: GLS Paket
   Letztes Update: 2026-05-29 08:18:02

3. DHL: 354482702077
   Status: registered
   Beschreibung: Dokumentenscanner
   Letztes Update: 2026-05-22 07:02:16

4. DHL: 00340434697726027444
   Status: Vorbereitung für Weitertransport
   Beschreibung: Bodylab Sirup
   Letztes Update: 2026-05-22 07:01:04

5. DHL: 00340434886264680017
   Status: elektronisch angekündigt
   Beschreibung: Aktuelle Sendung
   Letztes Update: 2026-05-15 08:57:24

6. DHL: JJD000390016899000548
   Status: abgeholt
   Beschreibung: Von Filiale abgeholt
   Letztes Update: 2026-05-06 14:06:49

[
  {
    "code": "[CODE]",
    "carrier": "hermes",
    "status": "registered",
    "description": "Beschreibung",
    "last_update": "2026-05-29 08:27:17"
  },
  {
    "code": "30027797654",
    "carrier": "gls",
    "status": "registered",
    "description": "GLS Paket",
    "last_update": "2026-05-29 08:18:02"
  },
  {
    "code": "354482702077",
    "carrier": "DHL",
    "status": "registered",
    "description": "Dokumentenscanner",
    "last_update": "2026-05-22 07:02:16"
  },
  {
    "code": "00340434697726027444",
    "carrier": "DHL",
    "status": "Vorbereitung für Weitertransport",
    "description": "Bodylab Sirup",
    "last_update": "2026-05-22 07:01:04"
  },
  {
    "code": "00340434886264680017",
    "carrier": "dhl",
    "status": "elektronisch angekündigt",
    "description": "Aktuelle Sendung",
    "last_update": "2026-05-15 08:57:24"
  },
  {
    "code": "JJD000390016899000548",
    "carrier": "dhl",
    "status": "abgeholt",
    "description": "Von Filiale abgeholt",
    "last_update": "2026-05-06 14:06:49"
  }
]

### Einzelnes Paket tracken

❌ Ungültige Tracking-Nummer: [TRACKING_CODE]
   Format: H gefolgt von 16+ Ziffern (z.B. [DEINE_TRACKING_NUMMER])

### Alle Pakete automatisch tracken



## Tracking-Nummern-Formate

| Carrier | Format | Beispiel |
|---------|--------|----------|
| DHL | 20 Ziffern / 12+ alphanumerisch |  |
| Hermes | H + 16+ Ziffern |  |
| GLS | 14 Ziffern (DE) / 11 Ziffern (IT) |  |
| DPD | *offen* | – |

## Status-Codes (alle Carrier)

| Code | Bedeutung |
|------|-----------|
|  | ✅ Zugestellt |
|  | 🚚 Im Zustellfahrzeug |
|  | 📦 Unterwegs |
|  | 📤 Abgeholt |
|  | 🏪 In Filiale |
|  | 📋 Elektronisch angekündigt |
|  | ⚠️ Problem/Verzögerung |

## Architektur



## Datenbank

- **Pfad:** 
- **Tabelle:**  – tracking_code, carrier, status, events, delivered
- **Automatische Verwaltung** durch 

## Automatisches Tracking (Cron)

[]

## Lizenz

MIT License
