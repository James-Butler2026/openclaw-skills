# newsletter-monitor

# Newsletter Monitor Skill v2.0

KI-gestützte Überwachung von Web.de Newsletter auf Fleisch- und Wurst-Angebote mit SQLite-Datenbank.

## Features

- **KI-Analyse** statt stumpfer Keywords - versteht Kontext und Produktkategorien
- **SQLite-Datenbank** - Keine Duplikate, Preisverlauf, bessere Struktur
- **Smarte Kategorisierung** - Fleisch, Wurst, Geflügel, Rind, Schwein
- **Preis-Tracking** - Historische Preise für bessere Deals

## Installation

### 1. .env Konfiguration
```bash
WEBDE_EMAIL=j_butler@web.de
WEBDE_PASSWORD=hgkuzg&(899JGVgf
WEBDE_IMAP_SERVER=imap.web.de
WEBDE_IMAP_PORT=993
WEBDE_USE_SSL=true
```

### 2. Datenbank
Wird automatisch erstellt bei erstem Lauf unter:
- `data/newsletter.db`

## Verwendung

### Manuell:
```bash
python3 scripts/webde_newsletter_monitor.py
```

### Ohne Telegram (Test):
```bash
python3 scripts/webde_newsletter_monitor.py --no-telegram
```

## Datenbank-Schema

### Tabellen:

**shops** - Bekannte Discounter
- id, name, email_pattern

**newsletters** - Alle empfangenen Newsletter
- id, message_id (unique), sender, subject, received_at, raw_content

**offers** - Extrahierte Angebote
- id, newsletter_id, shop_id, product_name
- price_current, price_original, price_per_100g, weight_g
- discount_percent, category (fleisch/wurst/geflügel/rind/schwein)
- valid_from/until, telegram_sent

**price_history** - Preisverlauf für Statistik
- id, offer_id, price, recorded_at

## KI-Analyse

### Erkennt automatisch:
- **Produktkategorie:** Fleisch, Wurst, Geflügel, Rind, Schwein
- **Preisformate:** 1,99€, 1.99€, €/100g, €/kg
- **Rabatte:** "statt X,XX€", "UVP", "nur"
- **Gewichte:** 500g, 1kg, 250g

### Unterstützte Shops:
- Netto, Lidl, Aldi, Rewe, Edeka, Penny, Kaufland

## Cron-Job

```
0 10 * * * TZ=Europe/Berlin cd /home/node/.openclaw/workspace && /home/node/.openclaw/venv/bin/python3 scripts/webde_newsletter_monitor.py >> /tmp/webde_newsletter.log 2>&1
```

Läuft täglich um **10:00 Uhr** (Europe/Berlin).

## Telegram Format

```
🥩 FLEISCH- & WURST-ANGEBOTE
📅 07.04.2026
📧 8 Angebote gefunden

🏪 Netto
──────────────────────────────

1. Schweine-Schnitzel
   💰 1.99€ (0.79€/100g) ⬇️ -25%
   ⚖️ 500g
   🏷️ Schwein

2. Hähnchenbrustfilet
   💰 3.49€ ⬇️ -15% ~~4.10€~~
   ⚖️ 1kg
   🏷️ Geflügel

🏪 Lidl
...

🎩 Ihr ergebener Butler James
```

## Dateien

- `scripts/webde_newsletter_monitor.py` - Hauptscript (v2.0)
- `data/newsletter.db` - SQLite-Datenbank
- `skills/newsletter-monitor/SKILL.md` - Diese Dokumentation

## Migration von v1

Die alte JSON-basierte Version wurde ersetzt:
- ✅ SQLite statt JSON-Dateien
- ✅ KI-Analyse statt Keywords
- ✅ Datenbank mit Historie
- ✅ Keine Duplikate mehr

---
*Version 2.0 - 07.04.2026 | KI-gestützte Angebotsanalyse*
