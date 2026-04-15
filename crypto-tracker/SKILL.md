---
name: crypto-tracker
description: Professioneller Portfolio-Tracker für Krypto-Investments (BTC, ETH, SOL, XRP). SQLite-basiert mit Gewinn/Verlust-Berechnung, Stop-Loss/Take-Profit Alerts, Durchschnittskosten, Performance-Vergleich und automatischen Reports.
---

# Crypto Portfolio Tracker

Ein professionelles Portfolio-Tracking-Tool für Krypto-Investments. Trackt Bitcoin (BTC), Ethereum (ETH), Solana (SOL) und Ripple (XRP) mit Echtzeit-Kursen und intelligenten Alerts.

## Features

- 💰 **Echtzeit-Kurse** via CoinGecko API (kostenlos, keine Auth nötig)
- 📊 **Gewinn/Verlust-Berechnung** in Echtzeit für alle 4 Coins
- 🎯 **Durchschnittskosten-Rechner** (gewichtet bei weiteren Käufen)
- 🚨 **Stop-Loss Warnung** bei -20% Verlust
- 🎯 **Take-Profit Alert** bei +25% Gewinn
- 🏆 **Performance-Vergleich** zwischen allen Coins (Rangliste)
- 📜 **Vollständige Trade-Historie**
- 🔘 **Telegram Inline-Buttons** für schnellen Zugriff
- 🔔 **Tägliche Updates** um 12:30 Uhr
- 📈 **Wochenbericht** am Sonntag

## Unterstützte Kryptowährungen

| Symbol | Name | CoinGecko ID |
|--------|------|--------------|
| BTC | Bitcoin | `bitcoin` |
| ETH | Ethereum | `ethereum` |
| SOL | Solana | `solana` |
| XRP | Ripple | `ripple` |

## Schnellstart

### Initialisierung
```bash
python3 scripts/crypto_tracker.py --init
```

### Verfügbare Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `--status` | Aktuellen Portfolio-Status anzeigen (alle 4 Coins) |
| `--daily` | Tägliches Update mit Snapshot |
| `--weekly` | Wochenbericht mit 7-Tage-Vergleich |
| `--hourly` | Stündlicher Check mit Alerts |
| `--history` | Trade-Historie anzeigen |
| `--performance` | Performance-Vergleich aller Coins (Rangliste) |
| `--buy COIN --amount X --eur Y` | Neuen Kauf hinzufügen |

### Beispiele

```bash
# Status prüfen (zeigt BTC, ETH, SOL, XRP)
python3 scripts/crypto_tracker.py --status

# Neuen Kauf hinzufügen (mit automatischer Durchschnittskosten-Berechnung)
python3 scripts/crypto_tracker.py --buy SOL --amount 0.7 --eur 50

# Performance-Vergleich (zeigt Rangliste aller Coins)
python3 scripts/crypto_tracker.py --performance

# Trade-Historie
python3 scripts/crypto_tracker.py --history
```

## Automatische Updates (Cron)

| Job | Zeit | Aktion |
|-----|------|--------|
| Stündlicher Check | Jede Stunde :00 | Prüft auf ±15% Bewegung, Stop-Loss -20%, Take-Profit +25% |
| Daily Update | 12:30 täglich | Vollständiger Status + Snapshot |
| Weekly Report | Sonntag 20:00 | 7-Tage Vergleich aller Coins |

## Alert-Logik

| Bedingung | Benachrichtigung |
|-----------|------------------|
| 🟢 Stündlich **+15%** | "SOL stündliche Bewegung: +16.2%" |
| 🔴 Stündlich **-15%** | "ETH stündliche Bewegung: -17.8%" |
| 🚨 **-20%** Gesamt | "STOP-LOSS: BTC bei -20.3%!" |
| 🎯 **+25%** Gesamt | "TAKE-PROFIT: XRP bei +26.1%!" |
| ✅ Normal (±14%) | **Keine Nachricht** (kein Spam) |

## Datenbank-Struktur

**Pfad:** `data/crypto_portfolio.db`

**Tabellen:**
- `holdings` - Aktuelle Bestände mit Durchschnittskosten für BTC, ETH, SOL, XRP
- `trades` - Alle Käufe/Verkäufe mit Zeitstempel
- `daily_snapshots` - Tägliche Wertaufzeichnungen pro Coin
- `hourly_prices` - Stündliche Preise für Bewegungs-Erkennung

## Telegram Integration

Alle Reports können automatisch in ein Telegram-Topic gepostet werden.

## Konfiguration

### Umgebungsvariablen

Keine API-Keys nötig – CoinGecko ist kostenlos und benötigt keine Authentifizierung.

### Anpassbare Schwellen (im Script)

```python
STOP_LOSS_PERCENT = -20      # Warnung bei -20%
HOURLY_ALERT_PERCENT = 15    # Alert bei ±15%
TAKE_PROFIT_PERCENT = 25     # Alert bei +25%
```

## Anforderungen

- Python 3.8+
- Internet-Verbindung (CoinGecko API)
- SQLite (in Python enthalten)

## CoinGecko API

**URL:** https://www.coingecko.com/en/api
- Kostenlos, keine Authentifizierung
- Rate Limit: ~10-30 Calls/Minute
- Unterstützt: BTC, ETH, SOL, XRP und 13.000+ weitere Coins

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Coin nicht gefunden" | Prüfe Symbol (BTC, ETH, SOL, XRP) |
| "Keine Kurse" | Internetverbindung prüfen |
| Falsche Berechnungen | Datenbank zurücksetzen mit `--init` |

---
*Verfügbar unter MIT-Lizenz*
