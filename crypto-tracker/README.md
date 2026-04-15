# Crypto Tracker

Professioneller Krypto-Portfolio-Tracker für Bitcoin (BTC), Ethereum (ETH), Solana (SOL) und Ripple (XRP).

## Features

- 💰 **Echtzeit-Kurse** via CoinGecko API
- 📊 **Gewinn/Verlust-Berechnung** für alle 4 Coins
- 🎯 **Durchschnittskosten-Rechner**
- 🚨 **Stop-Loss** (-20%) & **Take-Profit** (+25%) Alerts
- 🏆 **Performance-Vergleich** (Rangliste)
- 📜 **Trade-Historie**
- ⏰ **Automatische Reports** via Cron

## Unterstützte Coins

| Coin | Symbol | Typ |
|------|--------|-----|
| Bitcoin | BTC | Store of Value |
| Ethereum | ETH | Smart Contracts |
| Solana | SOL | High-Performance |
| Ripple | XRP | Banken/Transfers |

## Schnellstart

```bash
# Initialisieren
python3 scripts/crypto_tracker.py --init

# Status prüfen
python3 scripts/crypto_tracker.py --status

# Kauf hinzufügen
python3 scripts/crypto_tracker.py --buy ETH --amount 0.5 --eur 100
```

## Automatische Updates

| Job | Zeit |
|-----|------|
| Stündlich | Jede Stunde :00 |
| Daily | 12:30 täglich |
| Weekly | Sonntag 20:00 |

## API

**CoinGecko** - Kostenlos, keine Auth nötig
- Rate Limit: ~10-30 Calls/Minute
- URL: https://www.coingecko.com/en/api

## Lizenz

MIT License
