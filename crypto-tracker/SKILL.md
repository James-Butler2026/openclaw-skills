---
name: bison-tracker
description: Professioneller Portfolio-Tracker für Krypto-Investments (BTC, XRP, ETH, SOL). SQLite-basiert mit Gewinn/Verlust-Berechnung, Stop-Loss/Take-Profit Alerts, Durchschnittskosten, Performance-Vergleich, stündlichen Snapshots, Max/Min Gewinn-Tracking und automatischen Reports.
---

# Bison Portfolio Tracker v2.0

Ein professionelles Portfolio-Tracking-Tool für Krypto-Investments über die Bison-App und andere Börsen. Trackt Bitcoin (BTC), Ripple (XRP), Ethereum (ETH) und Solana (SOL) mit Echtzeit-Kursen, stündlicher Historie und intelligenten Alerts.

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
- ⏰ **Stündliche Snapshots** - speichert jeden Wert für spätere Analyse
- 📊 **Max-Gewinn-Tracking** - siehst du, wann du am meisten gewonnen hättest
- 📉 **Max-Verlust-Tracking** - siehst du, wann du am meisten verloren hättest

## Unterstützte Kryptowährungen

| Symbol | Name | CoinGecko ID |
|--------|------|--------------|
| BTC | Bitcoin | `bitcoin` |
| XRP | Ripple | `ripple` |
| ETH | Ethereum | `ethereum` |
| SOL | Solana | `solana` |

## Schnellstart

### Initialisierung
```bash
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --init
```

### Verfügbare Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `--status` | Aktuellen Portfolio-Status anzeigen (alle 4 Coins) |
| `--daily` | Tägliches Update mit Snapshot |
| `--weekly` | Wochenbericht mit 7-Tage-Vergleich |
| `--hourly` | Stündlicher Check mit Alerts + Speichern |
| `--max-profit` | Höchsten Gewinn seit Kauf anzeigen (pro Coin + Gesamt) |
| `--max-verlust` | Größten Verlust seit Kauf anzeigen (pro Coin + Gesamt) |
| `--history` | Trade-Historie anzeigen |
| `--performance` | Performance-Vergleich aller Coins (Rangliste) |
| `--buy COIN --amount X --eur Y` | Neuen Kauf hinzufügen |

### Beispiele

```bash
# Status prüfen (zeigt BTC, XRP, ETH, SOL)
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --status

# Höchsten Gewinn seit Kauf anzeigen
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --max-profit

# Größten Verlust seit Kauf anzeigen
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --max-verlust

# Neuen Kauf hinzufügen (mit automatischer Durchschnittskosten-Berechnung)
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --buy SOL --amount 0.7 --eur 50

# Performance-Vergleich (zeigt Rangliste aller Coins)
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --performance

# Trade-Historie
python3 skills/crypto-tracker/bison-tracker/scripts/bison_tracker.py --history
```

## Stündliche Snapshots (NEU in v2.0)

Der Tracker speichert **jede Stunde automatisch**:
- Aktuellen Portfolio-Wert
- Einzelpreise für alle Coins
- Gewinn/Verlust in € und %

**Vorteil:** Du kannst jederzeit nachschauen:
- Wann war mein Portfolio am höchsten? (`--max-profit`)
- Wann war mein Portfolio am niedrigsten? (`--max-verlust`)
- Welcher Coin performte am besten?
- Wie entwickelte sich der Markt über die Zeit?

## Automatische Updates (Cron)

| Job | Zeit | Aktion |
|-----|------|--------|
| Stündlicher Check | Jede Stunde :00 | Prüft auf ±15% Bewegung, Stop-Loss -20%, Take-Profit +25%. Speichert Snapshot. |
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
| 🏆 Neuer Höchstgewinn | **Keine Nachricht** (nur gespeichert) |

**Wichtig:** Der Höchstgewinn wird automatisch gespeichert, aber es gibt KEINE Alert-Nachricht. Du fragst ihn bei Bedarf mit `--max-profit` ab.

## Datenbank-Struktur

**Pfad:** `data/bison_portfolio.db`

**Tabellen:**
- `holdings` - Aktuelle Bestände mit Durchschnittskosten für BTC, XRP, ETH, SOL
- `trades` - Alle Käufe/Verkäufe mit Zeitstempel
- `daily_snapshots` - Tägliche Wertaufzeichnungen pro Coin
- `hourly_snapshots` - Stündliche Portfolio-Snapshots mit Gesamtwerten
- `hourly_prices` - Stündliche Preise für Bewegungs-Erkennung
- `max_profit_record` - Speichert den höchsten Gewinn aller Zeiten
- `max_loss_record` - Speichert den größten Verlust aller Zeiten
- `coin_max_min_prices` - Max/Min Preise seit Kauf für jeden Coin

## Telegram Integration

Alle Reports können automatisch in ein Telegram-Topic gepostet werden (z.B. Topic 1597 für Crypto-Updates).

Alerts werden NUR bei signifikanten Bewegungen gepostet:
- Stop-Loss / Take-Profit
- Stündliche Bewegungen > ±15%

**KEINE Spam-Nachrichten** bei neuen Höchstgewinnen - nur auf Anfrage (`--max-profit`).

## Konfiguration

### Umgebungsvariablen

Keine API-Keys nötig – CoinGecko ist kostenlos und benötigt keine Authentifizierung.

### Anpassbare Schwellen (im Script)

```python
STOP_LOSS_PERCENT = -20      # Warnung bei -20% Verlust
HOURLY_ALERT_PERCENT = 15    # Alert bei ±15% stündlich
TAKE_PROFIT_PERCENT = 25     # Alert bei +25% Gewinn
```

## Anforderungen

- Python 3.8+
- Internet-Verbindung (CoinGecko API)
- SQLite (in Python enthalten)

## CoinGecko API

**URL:** https://www.coingecko.com/en/api
- Kostenlos, keine Authentifizierung
- Rate Limit: ~10-30 Calls/Minute
- Unterstützt: BTC, ETH, XRP, SOL und 13.000+ weitere Coins

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Coin nicht gefunden" | Prüfe Symbol (BTC, ETH, XRP, SOL) |
| "Keine Kurse" | Internetverbindung prüfen |
| Falsche Berechnungen | Datenbank zurücksetzen mit `--init` |
| "Tabelle nicht gefunden" | `--init` ausführen um DB neu zu erstellen |

## Version History

### v2.0 (18.04.2026)
- ✨ Stündliche Snapshots
- ✨ Max-Gewinn-Tracking (`--max-profit`)
- ✨ Max-Verlust-Tracking (`--max-verlust`)
- ✨ Keine Alert-Spam bei Rekorden
- ✨ Pro-Coin Max/Min Preise seit Kauf

### v1.0
- Grundlegende Portfolio-Tracking
- Stop-Loss/Take-Profit Alerts
- Durchschnittskosten-Rechner

---
*Verfügbar unter MIT-Lizenz*
