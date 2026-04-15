# 🪙 Bison Tracker

Professioneller Krypto-Portfolio-Tracker für Bison-App-Nutzer. Trackt BTC und XRP mit Echtzeit-Kursen, automatischer Gewinn/Verlust-Berechnung und intelligenten Alerts.

## Features

- 💰 **Echtzeit-Kurse** via CoinGecko API (kostenlos)
- 📊 **Gewinn/Verlust-Berechnung** in Echtzeit
- 🎯 **Durchschnittskosten-Rechner** (automatisch bei weiteren Käufen)
- 🚨 **Stop-Loss Warnung** bei -20% Verlust
- 🎯 **Take-Profit Alert** bei +25% Gewinn
- 🏆 **Performance-Vergleich** (BTC vs XRP)
- 📜 **Vollständige Trade-Historie**
- ⏰ **Automatische Updates** via Cron

## Schnellstart

### Initialisierung
```bash
python3 scripts/bison_tracker.py --init
```

Dies erstellt die SQLite-Datenbank und fügt Beispiel-Daten hinzu.

## Befehle

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
# Aktuellen Status prüfen
python3 scripts/bison_tracker.py --status

# Neuen Kauf hinzufügen (mit automatischer Durchschnittskosten-Berechnung)
python3 scripts/bison_tracker.py --buy BTC --amount 0.001 --eur 65

# Performance-Vergleich
python3 scripts/bison_tracker.py --performance

# Trade-Historie ansehen
python3 scripts/bison_tracker.py --history
```

## Automatische Updates

### Cron-Jobs (empfohlen)

| Job | Zeit | Aktion |
|-----|------|--------|
| Stündlicher Check | Jede Stunde :00 | Prüft auf ±15% Bewegung, Stop-Loss -20%, Take-Profit +25% |
| Daily Update | 12:30 täglich | Vollständiger Status + Snapshot |
| Weekly Report | Sonntag 20:00 | 7-Tage Vergleich |

### Alert-Logik

- **±15% stündlich** → Alert (nur bei wilden Bewegungen)
- **-20% Gesamtverlust** → 🚨 Stop-Loss Warnung
- **+25% Gesamtgewinn** → 🎯 Take-Profit Alert
- **Normale Schwankungen** → Keine Meldung (kein Spam)

## Datenbank

**Pfad:** `data/bison_portfolio.db`

**Tabellen:**
- `holdings` - Aktuelle Bestände mit Durchschnittskosten
- `trades` - Alle Käufe/Verkäufe
- `daily_snapshots` - Tägliche Wertaufzeichnungen
- `hourly_prices` - Stündliche Preise für Bewegungs-Erkennung

## Telegram Integration

Alle Reports können automatisch in ein Telegram-Topic gepostet werden (z.B. Topic 1597).

## Anforderungen

- Python 3.8+
- Internet-Verbindung (CoinGecko API)
- SQLite (in Python enthalten)

## API

**CoinGecko** - Kostenlos, keine Authentifizierung nötig
- Rate Limit: ~10-30 Calls/Minute
- Dokumentation: https://www.coingecko.com/en/api

## Konfiguration

Editiere diese Werte im Script für andere Schwellen:

```python
STOP_LOSS_PERCENT = -20      # Warnung bei -20% Verlust
HOURLY_ALERT_PERCENT = 15    # Alert bei ±15% stündlich
TAKE_PROFIT_PERCENT = 25     # Alert bei +25% Gewinn
```

## Tipps

- **Keine Panik bei kurzfristigen Verlusten** - Crypto ist volatil
- **Stop-Loss ist ein Sicherheitsnetz** - nicht für 5% Tagesverluste
- **Durchschnittskosten helfen** beim Nachkaufen (DCA-Strategie)

---
*Erstellt für Eure Lordschaft* 🎩
