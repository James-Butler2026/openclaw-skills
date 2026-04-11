# Newsletter Monitor Skill

KI-gestützte Überwachung von Web.de Newsletter auf Fleisch-Angebote.

## Features

- 🤖 **KI-Analyse** statt stumpfer Keywords - versteht Kontext
- 💾 **SQLite-Datenbank** - Keine Duplikate, Preisverlauf
- 📊 **Smarte Kategorisierung** - Fleisch, Wurst, Geflügel, Rind, Schwein
- 💰 **Preis-Tracking** - Historische Preise für bessere Deals

## Schnellstart

```bash
# Manuell ausführen
python3 scripts/webde_newsletter_monitor.py

# Ohne Telegram (Test)
python3 scripts/webde_newsletter_monitor.py --no-telegram
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
# Web.de IMAP
WEBDE_EMAIL=deine_email@web.de
WEBDE_PASSWORD=dein_passwort
WEBDE_IMAP_SERVER=imap.web.de
WEBDE_IMAP_PORT=993
WEBDE_USE_SSL=true
```

## Automatische Überwachung

```cron
0 10 * * * TZ=Europe/Berlin cd /pfad/zum/workspace && python3 scripts/webde_newsletter_monitor.py
```

Läuft täglich um **10:00 Uhr** (Europe/Berlin).

## Erkannte Shops

- Netto, Lidl, Aldi, Rewe, Edeka, Penny, Kaufland

## Kategorien

- Fleisch, Wurst, Geflügel, Rind, Schwein

## Datenbank-Schema

- **shops** - Bekannte Discounter
- **newsletters** - Alle empfangenen Newsletter
- **offers** - Extrahierte Angebote mit Preisen
- **price_history** - Preisverlauf für Statistik

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
```

---

*Teil der OpenClaw Skills Collection* 🎩
