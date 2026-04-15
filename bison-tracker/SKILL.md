---
name: bison-tracker
description: Professioneller Portfolio-Tracker für Bison-Börsen-Investments (BTC, XRP). SQLite-basiert mit Stop-Loss, Performance-Vergleich, Durchschnittskosten, Trade-Historie und automatischen Reports.
---

# Bison Portfolio Tracker Skill

Professioneller Krypto-Portfolio-Tracker mit allen Features, die ein seriöser Investor braucht.

## Features

- 💰 **Echtzeit-Kurse** via CoinGecko API
- 📊 **Gewinn/Verlust-Berechnung** in Echtzeit
- 🎯 **Durchschnittskosten-Rechner** (gewichtet bei weiteren Käufen)
- 🚨 **Stop-Loss Warnung** bei -20% Verlust
- 🏆 **Performance-Vergleich** (BTC vs XRP)
- 📜 **Vollständige Trade-Historie**
- 🔘 **Telegram Inline-Buttons** für schnellen Zugriff
- 🔔 **Tägliche Updates** um 12:30 Uhr
- 📈 **Wochenbericht** am Sonntag

## Schnellstart

### Initialisierung
```bash
python3 skills/bison-tracker/scripts/bison_tracker.py --init
```

### Commands Übersicht

| Befehl | Beschreibung |
|--------|-------------|
| `--status` | Aktueller Portfolio-Status |
| `--daily` | Tägliches Update + Snapshot |
| `--weekly` | Wochenbericht mit 7-Tage-Vergleich |
| `--history` | Vollständige Trade-Historie |
| `--performance` | Performance-Vergleich BTC vs XRP |
| `--buy COIN --amount X --eur Y` | Neuen Kauf hinzufügen |
| `--buttons` | Verfügbare Telegram-Buttons anzeigen |

### Beispiele

```bash
# Status prüfen
python3 skills/bison-tracker/scripts/bison_tracker.py --status

# Neuen Kauf hinzufügen (mit Durchschnittskosten)
python3 skills/bison-tracker/scripts/bison_tracker.py --buy BTC --amount 0.001 --eur 65

# Trade-Historie
python3 skills/bison-tracker/scripts/bison_tracker.py --history

# Performance-Vergleich
python3 skills/bison-tracker/scripts/bison_tracker.py --performance
```

## Telegram Inline-Buttons

Nach jedem Update erscheinen Buttons:
```
[🔄 Aktualisieren] [📈 Wochenbericht] [📜 Historie]
[🏆 Performance] [💰 Status]
```

## Automatische Cron-Jobs

| Job | Zeit | Aktion |
|-----|------|--------|
| Daily Update | 12:30 täglich | Status + Snapshot + Alerts |
| Weekly Report | Sonntag 20:00 | 7-Tage-Vergleich |

## Datenbank-Struktur

**Tabellen:**
- `holdings` - Aktuelle Bestände mit Durchschnittskosten
- `trades` - Alle Käufe/Verkäufe
- `daily_snapshots` - Tägliche Wertaufzeichnungen
- `price_alerts` - Ausgelöste Alerts

## Stop-Loss & Alerts

- **-20% Verlust**: 🚨 Warnung wird angezeigt
- **Performance-Vergleich**: Zeigt besten/schlechtesten Coin
- **7-Tage-Vergleich**: Im Wochenbericht automatisch

---
*Skill erstellt für Eure Lordschaft* 🎩
