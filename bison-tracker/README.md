---
name: bison-tracker
description: Professionelles Krypto-Portfolio-Tracking für Bitcoin und Ripple (XRP). SQLite-basiert mit Gewinn/Verlust-Berechnung, automatischen Alerts und detaillierten Reports.
---

# Bison Tracker

Ein professionelles Portfolio-Tracking-Tool für Krypto-Investments über die Bison-App.

## Features

- 💰 **Echtzeit-Kurse** via CoinGecko API (kostenlos, keine Auth nötig)
- 📊 **Automatische Gewinn/Verlust-Berechnung** in Euro und Prozent
- 🎯 **Durchschnittskosten-Rechner** (gewichtet bei weiteren Käufen)
- 🚨 **Stop-Loss Warnung** bei -20% Verlust
- 🎯 **Take-Profit Alert** bei +25% Gewinn
- 🏆 **Performance-Vergleich** zwischen Coins
- 📜 **Vollständige Trade-Historie**
- ⏰ **Automatische Reports** via Cron

## Unterstützte Kryptowährungen

| Coin | Beschreibung |
|------|--------------|
| BTC (Bitcoin) | Store of Value, Digital Gold |
| XRP (Ripple) | Banken-Überweisungen, schnelle Transaktionen |

## Schnellstart

### Initialisierung
```bash
python3 scripts/bison_tracker.py --init
```

### Verfügbare Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `--status` | Aktuellen Portfolio-Status anzeigen |
| `--daily` | Tägliches Update mit Snapshot |
| `--weekly` | Wochenbericht mit 7-Tage-Vergleich |
| `--hourly` | Stündlicher Check (für Cron) |
| `--history` | Trade-Historie anzeigen |
| `--performance` | Performance-Vergleich BTC vs XRP |
| `--buy COIN --amount X --eur Y` | Neuen Kauf hinzufügen |

### Beispiele

```bash
# Status prüfen
python3 scripts/bison_tracker.py --status

# Neuen Kauf hinzufügen
python3 scripts/bison_tracker.py --buy BTC --amount 0.001 --eur 65

# Performance-Vergleich
python3 scripts/bison_tracker.py --performance
```

## Automatische Updates (Cron)

| Job | Zeit | Aktion |
|-----|------|--------|
| Stündlicher Check | Jede Stunde :00 | ±15% Bewegung, Stop-Loss, Take-Profit |
| Daily Update | 12:30 täglich | Vollständiger Status + Snapshot |
| Weekly Report | Sonntag 20:00 | 7-Tage Vergleich |

## Alert-Logik

- **±15% stündlich** → Alert (nur bei wilden Bewegungen)
- **-20% Gesamtverlust** → Stop-Loss Warnung
- **+25% Gesamtgewinn** → Take-Profit Alert
- **Normale Schwankungen** → Keine Meldung (kein Spam)

## Datenbank

**Pfad:** `data/bison_portfolio.db`

**Tabellen:**
- `holdings` - Aktuelle Bestände mit Durchschnittskosten
- `trades` - Alle Käufe/Verkäufe
- `daily_snapshots` - Tägliche Wertaufzeichnungen
- `hourly_prices` - Stündliche Preise für Bewegungs-Erkennung

## API

**CoinGecko** - Kostenlos, keine Authentifizierung
- Rate Limit: ~10-30 Calls/Minute
- Dokumentation: https://www.coingecko.com/en/api

## Konfiguration

```python
STOP_LOSS_PERCENT = -20      # Warnung bei -20%
HOURLY_ALERT_PERCENT = 15    # Alert bei ±15%
TAKE_PROFIT_PERCENT = 25     # Alert bei +25%
```

## Anforderungen

- Python 3.8+
- Internet-Verbindung (CoinGecko API)
- SQLite (in Python enthalten)

## Datenschutz

- Keine Daten in der Cloud
- Keine API-Keys nötig
- Lokale SQLite-Datenbank
- Einfach backuppen

---

*Verfügbar unter MIT-Lizenz*
