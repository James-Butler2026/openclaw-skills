#!/usr/bin/env python3
"""
Bison Portfolio Tracker - Erweiterte Version MIT STÜNDLICHEN SNAPSHOTS
Trackt BTC/XRP/ETH/SOL Investments mit Gewinn/Verlust-Berechnung, Stop-Loss, Performance-Vergleich, Trade-Historie, Durchschnittskosten
"""

import sqlite3
import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "bison_portfolio.db"
DATA_DIR = DB_PATH.parent

# Konfiguration
STOP_LOSS_PERCENT = -20  # Warnung bei -20% Verlust
ALERT_PERCENT = 5  # Benachrichtigung bei ±5% Bewegung seit letztem Check
HOURLY_ALERT_PERCENT = 15  # Stündlicher Alert nur bei ±15% (nicht zu nervig)
TAKE_PROFIT_PERCENT = 25  # Gewinn-Absicherung bei +25%


def init_db():
    """Initialisiert die SQLite Datenbank"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
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
    
    # STÜNDLICHE Snapshots - für genauen Höchstgewinn-Tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hourly_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_hour TEXT UNIQUE NOT NULL,
            total_invested REAL NOT NULL,
            total_value_eur REAL NOT NULL,
            total_profit_eur REAL NOT NULL,
            total_profit_percent REAL NOT NULL,
            btc_price REAL,
            xrp_price REAL,
            eth_price REAL,
            sol_price REAL,
            btc_value REAL,
            xrp_value REAL,
            eth_value REAL,
            sol_value REAL,
            snapshot_time TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Höchster Gewinn Tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS max_profit_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            max_profit_eur REAL NOT NULL,
            max_profit_percent REAL NOT NULL,
            timestamp_hour TEXT NOT NULL,
            btc_price REAL,
            xrp_price REAL,
            eth_price REAL,
            sol_price REAL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Alerts (für Preis-Bewegungen)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            trigger_price REAL,
            triggered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Datenbank initialisiert")


def get_crypto_prices():
    """Holt aktuelle Kurse von CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ripple,ethereum,solana&vs_currencies=usd,eur&include_24hr_change=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Kurse: {e}")
        return None


def add_trade(coin, amount, total_eur, price_usd=None):
    """Fügt neuen Trade hinzu und aktualisiert Durchschnittskosten"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    price_eur = total_eur / amount if amount > 0 else 0
    
    # In Trades speichern
    cursor.execute('''
        INSERT INTO trades (coin, type, amount, price_eur, price_usd, total_eur, timestamp)
        VALUES (?, 'buy', ?, ?, ?, ?, ?)
    ''', (coin, amount, price_eur, price_usd, total_eur, today))
    
    # Holdings aktualisieren mit Durchschnittskosten
    cursor.execute('SELECT amount, invested_eur, avg_buy_price, first_buy_date FROM holdings WHERE coin = ?', (coin,))
    existing = cursor.fetchone()
    
    if existing:
        old_amount, old_invested, old_avg, first_buy = existing
        new_amount = old_amount + amount
        new_invested = old_invested + total_eur
        # Neuer Durchschnittskaufpreis (gewichtet)
        new_avg = new_invested / new_amount if new_amount > 0 else 0
        
        cursor.execute('''
            UPDATE holdings 
            SET amount = ?, invested_eur = ?, avg_buy_price = ?, 
                last_buy_date = ?, updated_at = ?
            WHERE coin = ?
        ''', (new_amount, new_invested, new_avg, today, today, coin))
    else:
        # Erster Kauf
        avg_price = total_eur / amount
        cursor.execute('''
            INSERT INTO holdings (coin, amount, invested_eur, avg_buy_price, first_buy_date, last_buy_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (coin, amount, total_eur, avg_price, today, today, today, today))
    
    conn.commit()
    conn.close()
    print(f"✅ Trade hinzugefügt: {amount} {coin} für {total_eur:.2f}€ (Durchschnitt: {(total_eur/amount):.2f}€/{coin})")


def add_initial_holdings():
    """Fügt initiale Bestände hinzu"""
    # XRP: 100€ / 84.241025 XRP
    add_trade('XRP', 84.241025, 100.0)
    
    # BTC: 100€ / 0.00157188 BTC
    add_trade('BTC', 0.00157188, 100.0)
    
    # ETH: 70€ (50€ gekauft + 20€ geschenkt) / 0.03473428 ETH
    add_trade('ETH', 0.03473428, 70.0)
    
    # SOL: 50€ / 0.68268873 SOL
    add_trade('SOL', 0.68268873, 50.0)


def save_hourly_snapshot():
    """Speichert stündlichen Snapshot mit genauem Gewinn-Tracking"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT coin, amount, invested_eur, avg_buy_price FROM holdings')
    holdings = cursor.fetchall()
    
    prices = get_crypto_prices()
    if not prices:
        conn.close()
        return None
    
    coin_map = {
        'BTC': 'bitcoin',
        'XRP': 'ripple',
        'ETH': 'ethereum',
        'SOL': 'solana'
    }
    
    now = datetime.now()
    hour_key = now.strftime('%Y-%m-%d %H:00')
    
    total_invested = 0
    total_value = 0
    coin_values = {}
    coin_prices = {}
    
    for coin, amount, invested, avg_price in holdings:
        coin_id = coin_map.get(coin, coin.lower())
        price_data = prices.get(coin_id, {})
        price_eur = price_data.get('eur', 0)
        value_eur = amount * price_eur
        
        total_invested += invested
        total_value += value_eur
        coin_values[coin] = value_eur
        coin_prices[coin] = price_eur
    
    total_profit = total_value - total_invested
    total_profit_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    
    # Speichere stündlichen Snapshot
    cursor.execute('''
        INSERT OR REPLACE INTO hourly_snapshots 
        (timestamp_hour, total_invested, total_value_eur, total_profit_eur, total_profit_percent,
         btc_price, xrp_price, eth_price, sol_price,
         btc_value, xrp_value, eth_value, sol_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (hour_key, total_invested, total_value, total_profit, total_profit_pct,
          coin_prices.get('BTC', 0), coin_prices.get('XRP', 0), 
          coin_prices.get('ETH', 0), coin_prices.get('SOL', 0),
          coin_values.get('BTC', 0), coin_values.get('XRP', 0),
          coin_values.get('ETH', 0), coin_values.get('SOL', 0)))
    
    # Aktualisiere Max-Gewinn Record
    cursor.execute('SELECT MAX(max_profit_eur) FROM max_profit_record')
    current_max = cursor.fetchone()[0] or 0
    
    if total_profit > current_max:
        cursor.execute('''
            INSERT INTO max_profit_record 
            (max_profit_eur, max_profit_percent, timestamp_hour, btc_price, xrp_price, eth_price, sol_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (total_profit, total_profit_pct, hour_key,
              coin_prices.get('BTC', 0), coin_prices.get('XRP', 0),
              coin_prices.get('ETH', 0), coin_prices.get('SOL', 0)))
        conn.commit()
        conn.close()
        return {
            'new_record': True,
            'profit': total_profit,
            'percent': total_profit_pct,
            'hour': hour_key
        }
    
    conn.commit()
    conn.close()
    
    return {
        'new_record': False,
        'profit': total_profit,
        'percent': total_profit_pct,
        'hour': hour_key
    }


def get_max_profit_record():
    """Zeigt den höchsten Gewinn den du jemals hattest"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT max_profit_eur, max_profit_percent, timestamp_hour, btc_price, xrp_price, eth_price, sol_price
        FROM max_profit_record
        ORDER BY max_profit_eur DESC
        LIMIT 1
    ''')
    record = cursor.fetchone()
    
    # Hole letzte 3 Snapshots für Vergleich
    cursor.execute('''
        SELECT timestamp_hour, total_value_eur, total_profit_eur, total_profit_percent
        FROM hourly_snapshots
        ORDER BY timestamp_hour DESC
        LIMIT 3
    ''')
    recent = cursor.fetchall()
    
    conn.close()
    
    if not record:
        return None
    
    return {
        'max_profit': record[0],
        'max_percent': record[1],
        'timestamp': record[2],
        'prices': {'BTC': record[3], 'XRP': record[4], 'ETH': record[5], 'SOL': record[6]},
        'recent_snapshots': recent
    }


def check_hourly_alerts():
    """Prüft stündlich auf signifikante Preisbewegungen UND speichert Snapshot"""
    # Zuerst Snapshot speichern (das trackt auch Max-Gewinn)
    snapshot = save_hourly_snapshot()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT coin, amount, invested_eur, avg_buy_price FROM holdings')
    holdings = cursor.fetchall()
    conn.close()
    
    if not holdings:
        return []
    
    prices = get_crypto_prices()
    if not prices:
        return []
    
    alerts = []
    
    for coin, amount, invested, avg_price in holdings:
        coin_map = {'BTC': 'bitcoin', 'XRP': 'ripple', 'ETH': 'ethereum', 'SOL': 'solana'}
        coin_id = coin_map.get(coin, coin.lower())
        current_price = prices.get(coin_id, {}).get('eur', 0)
        
        current_value = amount * current_price
        total_profit_percent = ((current_value - invested) / invested) * 100 if invested > 0 else 0
        
        # Prüfe Stop-Loss
        if total_profit_percent <= STOP_LOSS_PERCENT:
            alerts.append(f"🚨 STOP-LOSS: {coin} bei {total_profit_percent:.1f}%! (Kurs: {current_price:.2f}€)")
        
        # Prüfe Take-Profit
        if total_profit_percent >= TAKE_PROFIT_PERCENT:
            alerts.append(f"🎯 TAKE-PROFIT: {coin} bei +{total_profit_percent:.1f}%! (Kurs: {current_price:.2f}€)")
    
    # Wenn neuer Rekord, füge Info hinzu
    if snapshot and snapshot.get('new_record'):
        alerts.append(f"🏆 NEUER HÖCHSTGEWINN: {snapshot['profit']:+.2f}€ ({snapshot['percent']:+.2f}%) @ {snapshot['hour']}")
    
    return alerts


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Bison Portfolio Tracker')
    parser.add_argument('--init', action='store_true', help='Datenbank initialisieren')
    parser.add_argument('--status', action='store_true', help='Aktuellen Status anzeigen')
    parser.add_argument('--daily', action='store_true', help='Tägliches Update mit Snapshot')
    parser.add_argument('--weekly', action='store_true', help='Wochenbericht')
    parser.add_argument('--history', action='store_true', help='Trade-Historie anzeigen')
    parser.add_argument('--performance', action='store_true', help='Performance-Vergleich')
    parser.add_argument('--hourly', action='store_true', help='Stündlicher Check mit Alerts + Snapshot')
    parser.add_argument('--max-profit', action='store_true', dest='max_profit', help='Höchsten Gewinn anzeigen')
    parser.add_argument('--buy', metavar='COIN', help='Neuen Kauf hinzufügen (BTC/XRP)')
    parser.add_argument('--amount', type=float, help='Menge')
    parser.add_argument('--eur', type=float, help='Investierter Betrag in EUR')
    
    args = parser.parse_args()
    
    if args.init:
        init_db()
        add_initial_holdings()
        return 0
    
    if not DB_PATH.exists():
        print("❌ Datenbank nicht gefunden. Führe zuerst --init aus.")
        return 1
    
    if args.buy:
        if not args.amount or not args.eur:
            print("❌ Fehlende Parameter: --amount und --eur erforderlich")
            return 1
        add_trade(args.buy.upper(), args.amount, args.eur)
        return 0
    
    if args.hourly:
        # Stündlicher Check mit Alert-Erkennung + Snapshot
        alerts = check_hourly_alerts()
        if alerts:
            print("\n⚠️ SIGNIFIKANTE BEWEGUNGEN ERKANNT:\n")
            for alert in alerts:
                print(f"   {alert}")
            print("\n" + "─" * 65)
            return 1
        else:
            print("✅ Keine signifikanten Bewegungen (±15% oder Stop-Loss/Take-Profit nicht erreicht)")
            return 0
    
    elif args.max_profit:
        record = get_max_profit_record()
        if record:
            print(f"\n🏆 HÖCHSTER GEWINN DEN DU HATTES:")
            print(f"   💰 Gewinn: {record['max_profit']:+.2f}€ ({record['max_percent']:+.2f}%)")
            print(f"   📅 Zeitpunkt: {record['timestamp']}")
            print(f"\n📊 Preise zu diesem Zeitpunkt:")
            for coin, price in record['prices'].items():
                print(f"   {coin}: {price:,.2f}€")
            print(f"\n📈 Letzte Stunden:")
            for snap in record['recent_snapshots']:
                print(f"   {snap[0]}: {snap[2]:+.2f}€ ({snap[3]:+.2f}%)")
        else:
            print("❌ Noch keine Daten vorhanden. Führe zuerst --hourly aus.")
        return 0
    
    else:
        print("Verwendung: bison_tracker.py [--init|--hourly|--max-profit|--buy COIN --amount X --eur Y]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
