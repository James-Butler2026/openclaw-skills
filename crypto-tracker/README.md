# Crypto Tracker Skill

Krypto-Portfolio-Tracking für BTC, ETH, SOL, XRP mit Gewinn/Verlust-Berechnung.

## Features

- 📈 Echtzeit-Kurse via CoinGecko API
- 💰 Gewinn/Verlust-Berechnung
- 🚨 Stop-Loss bei -20%, Take-Profit bei +25%
- 📊 Performance-Vergleich
- 💾 SQLite-basiert

## Installation

```bash
cd ~/.openclaw/workspace/skills/crypto-tracker/
```

## Verwendung

```bash
# Portfolio initialisieren
python3 scripts/crypto_tracker.py --init

# Status anzeigen
python3 scripts/crypto_tracker.py --status

# Preisalarme prüfen
python3 scripts/crypto_tracker.py --alerts
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
# Optional: CoinGecko API Key für höhere Limits
COINGECKO_API_KEY=dein_key_hier
```

## Sicherheit

- Keine Wallet-Keys oder Private Keys im System
- Nur Preis-Tracking, kein Trading
- Daten bleiben lokal

---
*Krypto-Portfolio-Tracking für OpenClaw* 📈
