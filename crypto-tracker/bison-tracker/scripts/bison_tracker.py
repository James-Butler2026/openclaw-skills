#!/usr/bin/env python3
"""
Bison Portfolio Tracker v2.1 - OPTIMIERT mit Error Handling & Logging
Trackt BTC/XRP/ETH/SOL Investments mit Gewinn/Verlust-Berechnung, Stop-Loss, Performance-Vergleich

Verbesserungen v2.1:
- ✅ Error Handling bei allen API Calls
- ✅ Logging statt print()
- ✅ Backup vor --init
- ✅ Konfiguration aus config.json
- ✅ Robuste Datenbank-Verbindungen
"""

import sqlite3
import json
import urllib.request
import urllib.error
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, Optional, Tuple, List

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path('/tmp/bison_tracker.log'))
    ]
)
logger = logging.getLogger(__name__)

# Pfade
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "bison_portfolio.db"
DATA_DIR = DB_PATH.parent
CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> Dict:
    """Lädt Konfiguration aus JSON oder erstellt Standard"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
    
    # Standard-Konfiguration
    default_config = {
        "stop_loss_percent": -20,
        "take_profit_percent": 25,
        "hourly_alert_percent": 15,
        "coins": {
            "BTC": {"id": "bitcoin", "name": "Bitcoin"},
            "XRP": {"id": "ripple", "name": "Ripple"},
            "ETH": {"id": "ethereum", "name": "Ethereum"},
            "SOL": {"id": "solana", "name": "Solana"}
        }
    }
    
    # Speichere Standard-Konfiguration
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info(f"Standard-Konfiguration erstellt: {CONFIG_FILE}")
    except IOError as e:
        logger.error(f"Konnte Konfiguration nicht speichern: {e}")
    
    return default_config

CONFIG = load_config()

def backup_db() -> Optional[Path]:
    """Erstellt Backup der Datenbank vor wichtigen Operationen"""
    if not DB_PATH.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f'.backup.{timestamp}.db')
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"✅ Datenbank-Backup erstellt: {backup_path}")
        return backup_path
    except IOError as e:
        logger.error(f"❌ Backup fehlgeschlagen: {e}")
        return None

def init_db(force: bool = False) -> bool:
    """Initialisiert die SQLite Datenbank
    
    Args:
        force: Wenn True, wird DB trotzdem neu erstellt (mit Backup!)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Backup vor Neuerstellung
        if DB_PATH.exists() and not force:
            logger.warning("⚠️  Datenbank existiert bereits!")
            logger.info("💡 Verwende --force zum Neuerstellen (Backup wird erstellt)")
            return False
        
        if DB_PATH.exists() and force:
            backup_path = backup_db()
            if backup_path:
                logger.info(f"💾 Backup vor Neuerstellung: {backup_path}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Bestände mit Durchschnittskosten
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                invested_eur REAL NOT NULL DEFAULT 0,
                avg_buy_price REAL DEFAULT 0,
                bison_price_usd REAL,
                first_buy_date TEXT,
                last_buy_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                price_eur REAL NOT NULL,
                price_usd REAL,
                total_eur REAL NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tägliche Snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                amount REAL NOT NULL,
                price_usd REAL NOT NULL,
                price_eur REAL NOT NULL,
                value_eur REAL NOT NULL,
                profit_loss_eur REAL,
                profit_loss_percent REAL,
                snapshot_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # STÜNDLICHE Snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hourly_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_hour TEXT UNIQUE NOT NULL,
                total_invested REAL NOT NULL,
                total_value_eur REAL NOT NULL,
                total_profit_eur REAL NOT NULL,
                total_profit_percent REAL NOT NULL,
                btc_price REAL, xrp_price REAL, eth_price REAL, sol_price REAL,
                btc_value REAL, xrp_value REAL, eth_value REAL, sol_value REAL,
                snapshot_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Höchster Gewinn/Verlust Tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS max_profit_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_profit_eur REAL NOT NULL,
                max_profit_percent REAL NOT NULL,
                timestamp_hour TEXT NOT NULL,
                btc_price REAL, xrp_price REAL, eth_price REAL, sol_price REAL,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS max_loss_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_loss_eur REAL NOT NULL,
                max_loss_percent REAL NOT NULL,
                timestamp_hour TEXT NOT NULL,
                btc_price REAL, xrp_price REAL, eth_price REAL, sol_price REAL,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Coin-spezifische Max/Min
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_max_min_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT UNIQUE NOT NULL,
                max_price_since_buy REAL NOT NULL,
                max_price_timestamp TEXT NOT NULL,
                max_profit_eur REAL NOT NULL,
                max_profit_percent REAL NOT NULL,
                min_price_since_buy REAL NOT NULL,
                min_price_timestamp TEXT NOT NULL,
                min_profit_eur REAL NOT NULL,
                min_profit_percent REAL NOT NULL,
                avg_buy_price REAL NOT NULL,
                amount REAL NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Datenbank initialisiert")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Datenbank-Fehler: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {e}")
        return False

def get_crypto_prices() -> Optional[Dict]:
    """Holt aktuelle Kurse von CoinGecko mit Retry"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            coin_ids = ",".join([c["id"] for c in CONFIG["coins"].values()])
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd,eur&include_24hr_change=true"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                logger.debug("✅ Kurse erfolgreich abgerufen")
                return data
                
        except urllib.error.URLError as e:
            logger.warning(f"API-Fehler (Versuch {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential Backoff
            else:
                logger.error("❌ Alle API-Versuche fehlgeschlagen")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ungültige JSON-Antwort: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}")
            return None
    
    return None

def add_trade(coin: str, amount: float, total_eur: float, price_usd: Optional[float] = None) -> bool:
    """Fügt neuen Trade hinzu und aktualisiert Durchschnittskosten"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        price_eur = total_eur / amount if amount > 0 else 0
        
        # In Trades speichern
        cursor.execute('''
            INSERT INTO trades (coin, type, amount, price_eur, price_usd, total_eur, timestamp)
            VALUES (?, 'buy', ?, ?, ?, ?, ?)
        ''', (coin, amount, price_eur, price_usd, total_eur, today))
        
        # Holdings aktualisieren
        cursor.execute('SELECT amount, invested_eur, avg_buy_price, first_buy_date FROM holdings WHERE coin = ?', (coin,))
        existing = cursor.fetchone()
        
        if existing:
            old_amount, old_invested, old_avg, first_buy = existing
            new_amount = old_amount + amount
            new_invested = old_invested + total_eur
            new_avg = new_invested / new_amount if new_amount > 0 else 0
            
            cursor.execute('''
                UPDATE holdings 
                SET amount = ?, invested_eur = ?, avg_buy_price = ?, last_buy_date = ?
                WHERE coin = ?
            ''', (new_amount, new_invested, new_avg, today, coin))
        else:
            cursor.execute('''
                INSERT INTO holdings (coin, amount, invested_eur, avg_buy_price, first_buy_date, last_buy_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (coin, amount, total_eur, price_eur, today, today))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Trade hinzugefügt: {coin} {amount} zu {total_eur}€")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ DB-Fehler beim Trade: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Fehler beim Trade: {e}")
        return False

def get_portfolio_status() -> Optional[Dict]:
    """Holt aktuellen Portfolio-Status"""
    try:
        prices = get_crypto_prices()
        if not prices:
            return None
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT coin, amount, invested_eur, avg_buy_price FROM holdings WHERE amount > 0')
        holdings = cursor.fetchall()
        conn.close()
        
        if not holdings:
            logger.info("📊 Keine Holdings gefunden")
            return None
        
        portfolio = {}
        total_invested = 0
        total_value = 0
        
        for coin, amount, invested, avg_buy in holdings:
            coin_lower = coin.lower()
            price_data = prices.get(CONFIG["coins"][coin]["id"], {})
            current_price = price_data.get('eur', 0)
            
            value = amount * current_price
            profit = value - invested
            profit_percent = (profit / invested * 100) if invested > 0 else 0
            
            portfolio[coin] = {
                'amount': amount,
                'invested': invested,
                'avg_buy': avg_buy,
                'current_price': current_price,
                'value': value,
                'profit': profit,
                'profit_percent': profit_percent
            }
            
            total_invested += invested
            total_value += value
        
        total_profit = total_value - total_invested
        total_profit_percent = (total_profit / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'coins': portfolio,
            'total_invested': total_invested,
            'total_value': total_value,
            'total_profit': total_profit,
            'total_profit_percent': total_profit_percent
        }
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Status: {e}")
        return None

def check_alerts(status: Dict) -> List[str]:
    """Prüft auf Alerts (Stop-Loss, Take-Profit)"""
    alerts = []
    
    try:
        # Stop-Loss
        if status['total_profit_percent'] <= CONFIG['stop_loss_percent']:
            alerts.append(f"🚨 STOP-LOSS: Portfolio bei {status['total_profit_percent']:.1f}%!")
        
        # Take-Profit
        if status['total_profit_percent'] >= CONFIG['take_profit_percent']:
            alerts.append(f"🎯 TAKE-PROFIT: Portfolio bei +{status['total_profit_percent']:.1f}%!")
        
        # Pro-Coin Checks
        for coin, data in status['coins'].items():
            if data['profit_percent'] <= CONFIG['stop_loss_percent']:
                alerts.append(f"🚨 STOP-LOSS: {coin} bei {data['profit_percent']:.1f}%!")
            elif data['profit_percent'] >= CONFIG['take_profit_percent']:
                alerts.append(f"🎯 TAKE-PROFIT: {coin} bei +{data['profit_percent']:.1f}%!")
        
        return alerts
        
    except Exception as e:
        logger.error(f"❌ Fehler bei Alerts: {e}")
        return []

def format_portfolio_report(status: Dict) -> str:
    """Formattiert Portfolio-Status für Ausgabe"""
    try:
        lines = [
            "📊 **DAILY CRYPTO REPORT**",
            f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            "",
            "💰 Aktuelle Preise:"
        ]
        
        # Preise
        for coin in ['BTC', 'XRP', 'ETH', 'SOL']:
            if coin in status['coins']:
                price = status['coins'][coin]['current_price']
                lines.append(f"   {coin}: {price:,.2f} €")
        
        lines.append("")
        
        # Einzel-Coins
        for coin, data in status['coins'].items():
            emoji = "🟢" if data['profit'] >= 0 else "🔴"
            lines.extend([
                f"🪙 **{coin}:**",
                f"   Bestand: {data['amount']:.8f}",
                f"   Investiert: {data['invested']:.2f} €",
                f"   Ø Kaufpreis: {data['avg_buy']:.2f} €",
                f"   Wert: {data['value']:.2f} €",
                f"   {emoji} P/L: {data['profit']:+.2f} € ({data['profit_percent']:+.2f}%)",
                ""
            ])
        
        # Gesamt
        total_emoji = "🟢" if status['total_profit'] >= 0 else "🔴"
        lines.extend([
            "=" * 50,
            "💰 **GESAMT:**",
            f"   Investiert: {status['total_invested']:.2f} €",
            f"   Aktueller Wert: {status['total_value']:.2f} €",
            f"   {total_emoji} **Gewinn/Verlust: {status['total_profit']:+.2f} € ({status['total_profit_percent']:+.2f}%)**"
        ])
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Formatieren: {e}")
        return f"❌ Fehler: {e}"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Bison Portfolio Tracker v2.1')
    parser.add_argument('--init', action='store_true', help='Datenbank initialisieren (mit Backup!)')
    parser.add_argument('--force', action='store_true', help='Neuerstellung erzwingen (Backup wird erstellt)')
    parser.add_argument('--status', action='store_true', help='Portfolio-Status anzeigen')
    parser.add_argument('--daily', action='store_true', help='Täglicher Report')
    parser.add_argument('--buy', metavar='COIN', help='Neuen Kauf hinzufügen')
    parser.add_argument('--amount', type=float, help='Menge des Coins')
    parser.add_argument('--eur', type=float, help='Investierter Betrag in EUR')
    parser.add_argument('--backup', action='store_true', help='Manuelles Backup erstellen')
    
    args = parser.parse_args()
    
    if args.backup:
        backup_path = backup_db()
        if backup_path:
            print(f"✅ Backup erstellt: {backup_path}")
        return
    
    if args.init:
        if init_db(force=args.force):
            print("✅ Datenbank initialisiert")
        return
    
    if args.buy:
        if not args.amount or not args.eur:
            print("❌ --amount und --eur erforderlich für --buy")
            return
        if add_trade(args.buy.upper(), args.amount, args.eur):
            print(f"✅ Kauf hinzugefügt: {args.buy} {args.amount} für {args.eur}€")
        return
    
    if args.status or args.daily:
        status = get_portfolio_status()
        if status:
            report = format_portfolio_report(status)
            print(report)
            
            # Alerts prüfen
            alerts = check_alerts(status)
            for alert in alerts:
                print(f"\n{alert}")
        else:
            print("❌ Konnte Portfolio-Status nicht abrufen")
        return
    
    parser.print_help()

if __name__ == "__main__":
    main()
