---
name: gls-tracking
description: GLS Paketverfolgung via gls-group.eu öffentlichem REST-Endpoint. Kein API-Key nötig.
---

# GLS Sendungsverfolgung

Automatisierte GLS-Paketverfolgung via öffentlichem REST-Endpoint von gls-group.eu.
**Kein API-Key nötig!**

## Features

- 🚫 **Kein API-Key** – Nutzt öffentlichen GLS-REST-Endpoint
- 🌐 **Deutschland & International** – Funktioniert für GLS EU-Netzwerk
- 📦 **Automatische Überwachung** – Erkennt Status-Änderungen
- 📱 **Telegram-Benachrichtigung** – über package_manager.py
- 📊 **JSON-Output** – Für Weiterverarbeitung
- 🔗 **URL-Erkennung** – Kann ganze Tracking-Links verarbeiten

## Tracking-Nummern-Formate

| Format | Beispiel | Beschreibung |
|--------|----------|--------------|
| 14 Ziffern | `12345678901234` | Standard Deutschland |
| 12-16 Ziffern | `123456789012` | Numerisch (EU) |
| 8-12 alphanumerisch | `AB12CD34` | Kurzform |
| International | `GL123456789DE` | 2 Buchstaben + 9 Ziffern + 2 Länderkürzel |

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
python3 scripts/gls_tracker.py 12345678901234

# JSON-Output
python3 scripts/gls_tracker.py 12345678901234 --json

# Mit URL
python3 scripts/gls_tracker.py "https://gls-group.com/DE/de/parcel-tracking?match=12345678901234"

# Nur Ergebnisse (kein Header)
python3 scripts/gls_tracker.py 12345678901234 --quiet
```

### Beispiel-Output

```
============================================================
📦 GLS SENDUNGSSTATUS
📦 12345678901234
============================================================

✅ Status: DELIVERED
   Code: delivered
📅 Voraussichtliche Zustellung: 2026-05-28

📋 Letzte Updates:
   • 2026-05-28T14:30: Die Sendung wurde zugestellt (Berlin)
   • 2026-05-28T08:15: Die Sendung ist im Zustellfahrzeug (Berlin)
   • 2026-05-27T22:00: Die Sendung ist im Paketzentrum (Berlin)
============================================================
```

### Automatische Überwachung (via package_manager.py)

```bash
# Paket hinzufügen
python3 skills/hermes-tracking/scripts/package_manager.py add \
    --code 12345678901234 \
    --carrier gls \
    --desc "Mein GLS Paket"

# Alle Pakete tracken (DHL + Hermes + GLS)
python3 skills/hermes-tracking/scripts/package_manager.py track --json
```

## Status-Codes

| Code | Bedeutung | Emoji |
|------|-----------|-------|
| `delivered` | Zugestellt | ✅ |
| `in_delivery` | Im Zustellfahrzeug | 🚚 |
| `in_transit` | Unterwegs / im Paketzentrum | 📦 |
| `picked_up` | Abgeholt | 📤 |
| `in_store` | In Filiale / PaketShop | 🏪 |
| `announced` | Elektronisch angekündigt | 📋 |
| `exception` | Problem / Verzögerung | ⚠️ |
| `unknown` | Nicht ermittelbar | ❓ |

## API-Details

- **URL:** `https://gls-group.eu/app/service/search/rest/de/de/routing/parcel?search={NR}`
- **Method:** GET
- **Headers:** Normale Browser-Headers
- **Response:** JSON mit Sendungsdetails
- **Keine Authentifizierung nötig!**

## Integration ins bestehende System

Das Modul ist vollständig in den existierenden package_manager integriert:

- `package_manager.py add --carrier gls` → Fügt GLS-Paket hinzu
- `package_manager.py track` → Trackt automatisch ALLE Pakete (DHL + Hermes + GLS)
- `db_manager.py` → Tracking-URL wird automatisch generiert

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Ungültige Tracking-Nummer" | Format prüfen (14 Ziffern?) |
| "HTTP Fehler 500" | GLS Server – ungültige Nummer oder temporär nicht erreichbar |
| "Verbindungsfehler" | Internet prüfen, erneut versuchen |

## Unterschied zu Hermes (Browser + OCR)

| Feature | Hermes | GLS | DHL |
|---------|--------|-----|-----|
| API-Key nötig | ❌ | ❌ | ❌ |
| Browser nötig | ✅ (Playwright) | ❌ | ❌ |
| OCR nötig | ✅ (Tesseract) | ❌ | ❌ |
| Abhängigkeiten | Playwright, Tesseract, Pillow | **Keine** (nur stdlib) | **Keine** (nur stdlib) |
| Geschwindigkeit | Langsam (~30s) | **Schnell (~2s)** | Schnell (~2s) |

## Lizenz

MIT License – Open Source, frei nutzbar.

---

**Hinweis:** Nutzt den öffentlichen REST-Endpoint von gls-group.eu. Keine offizielle GLS API-Integration.
