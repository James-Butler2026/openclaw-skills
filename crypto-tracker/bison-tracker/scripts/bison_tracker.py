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
    """Initialisiert die SQLite Datenbank
    
    ⚠️  WICHTIG: NUR bei erstmaligem Setup verwenden!
    ⚠️  NIE auf bestehender DB ausführen - ALLE Daten gehen verloren!
    ⚠️  Für neue Käufe: --buy COIN --amount X --eur Y verwenden!
    
    BEI ZWEIFEL: Erst fragen, nie --init auf bestehende DB!
    """
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
    
    # Höchster Gewinn Tracking (Gesamtportfolio)
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
    
    # GRÖSSTER VERLUST Tracking (Gesamtportfolio)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS max_loss_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            max_loss_eur REAL NOT NULL,
            max_loss_percent REAL NOT NULL,
            timestamp_hour TEXT NOT NULL,
            btc_price REAL,
            xrp_price REAL,
            eth_price REAL,
            sol_price REAL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # COIN-SPEZIFISCHE Max/Min Preise seit Kauf
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
    
    # Aktualisiere Max-Gewinn Record (Gesamtportfolio)
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
        new_record = True
    else:
        new_record = False
    
    # Aktualisiere Max-VERLUST Record (Gesamtportfolio) - tiefster rote Zahl
    cursor.execute('SELECT MIN(max_loss_eur) FROM max_loss_record')
    current_min = cursor.fetchone()[0] or 0
    
    if total_profit < current_min:
        cursor.execute('''
            INSERT INTO max_loss_record 
            (max_loss_eur, max_loss_percent, timestamp_hour, btc_price, xrp_price, eth_price, sol_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (total_profit, total_profit_pct, hour_key,
              coin_prices.get('BTC', 0), coin_prices.get('XRP', 0),
              coin_prices.get('ETH', 0), coin_prices.get('SOL', 0)))
        new_loss_record = True
    else:
        new_loss_record = False
    
    # Aktualisiere COIN-SPEZIFISCHE Max/Min Preise seit Kauf
    for coin, amount, invested, avg_price in holdings:
        if amount <= 0 or avg_price <= 0:
            continue
            
        coin_id = coin_map.get(coin, coin.lower())
        current_price = coin_prices.get(coin, 0)
        
        # Berechne Gewinn/Verlust bei aktuellem Preis
        current_value = amount * current_price
        current_profit = current_value - invested
        current_profit_pct = ((current_price - avg_price) / avg_price) * 100
        
        # Hole bestehende Max/Min Daten
        cursor.execute('SELECT max_price_since_buy, min_price_since_buy FROM coin_max_min_prices WHERE coin = ?', (coin,))
        existing = cursor.fetchone()
        
        if existing:
            existing_max, existing_min = existing
            
            # Update Max
            new_max = max(existing_max, current_price) if existing_max else current_price
            new_max_timestamp = hour_key if new_max == current_price else None
            max_profit = amount * new_max - invested
            max_profit_pct = ((new_max - avg_price) / avg_price) * 100
            
            # Update Min
            new_min = min(existing_min, current_price) if existing_min else current_price
            new_min_timestamp = hour_key if new_min == current_price else None
            min_profit = amount * new_min - invested
            min_profit_pct = ((new_min - avg_price) / avg_price) * 100
            
            cursor.execute('''
                UPDATE coin_max_min_prices SET
                    max_price_since_buy = ?,
                    max_price_timestamp = COALESCE(?, max_price_timestamp),
                    max_profit_eur = ?,
                    max_profit_percent = ?,
                    min_price_since_buy = ?,
                    min_price_timestamp = COALESCE(?, min_price_timestamp),
                    min_profit_eur = ?,
                    min_profit_percent = ?,
                    updated_at = ?
                WHERE coin = ?
            ''', (new_max, new_max_timestamp, max_profit, max_profit_pct,
                  new_min, new_min_timestamp, min_profit, min_profit_pct,
                  hour_key, coin))
        else:
            # Erste Eintragung für diesen Coin
            cursor.execute('''
                INSERT INTO coin_max_min_prices 
                (coin, max_price_since_buy, max_price_timestamp, max_profit_eur, max_profit_percent,
                 min_price_since_buy, min_price_timestamp, min_profit_eur, min_profit_percent,
                 avg_buy_price, amount, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (coin, current_price, hour_key, current_profit, current_profit_pct,
                  current_price, hour_key, current_profit, current_profit_pct,
                  avg_price, amount, hour_key))
    
    conn.commit()
    conn.close()
    
    return {
        'new_record': new_record,
        'profit': total_profit,
        'percent': total_profit_pct,
        'hour': hour_key
    }


def get_max_profit_record():
    """Zeigt den höchsten Gewinn den du jemals hattest (Gesamt + pro Coin)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Gesamtportfolio
    cursor.execute('''
        SELECT max_profit_eur, max_profit_percent, timestamp_hour, btc_price, xrp_price, eth_price, sol_price
        FROM max_profit_record
        ORDER BY max_profit_eur DESC
        LIMIT 1
    ''')
    total_record = cursor.fetchone()
    
    # Coin-spezifische Max/Min
    cursor.execute('''
        SELECT coin, max_price_since_buy, max_price_timestamp, max_profit_eur, max_profit_percent,
               min_price_since_buy, min_price_timestamp, min_profit_eur, min_profit_percent,
               avg_buy_price, amount
        FROM coin_max_min_prices
        ORDER BY coin
    ''')
    coin_records = cursor.fetchall()
    
    # Letzte 3 Snapshots
    cursor.execute('''
        SELECT timestamp_hour, total_value_eur, total_profit_eur, total_profit_percent
        FROM hourly_snapshots
        ORDER BY timestamp_hour DESC
        LIMIT 3
    ''')
    recent = cursor.fetchall()
    
    conn.close()
    
    result = {
        'total': None,
        'coins': {},
        'recent_snapshots': recent
    }
    
    if total_record:
        result['total'] = {
            'max_profit': total_record[0],
            'max_percent': total_record[1],
            'timestamp': total_record[2],
            'prices': {'BTC': total_record[3], 'XRP': total_record[4], 'ETH': total_record[5], 'SOL': total_record[6]}
        }
    
    for row in coin_records:
        coin = row[0]
        result['coins'][coin] = {
            'max_price': row[1],
            'max_timestamp': row[2],
            'max_profit_eur': row[3],
            'max_profit_pct': row[4],
            'min_price': row[5],
            'min_timestamp': row[6],
            'min_profit_eur': row[7],
            'min_profit_pct': row[8],
            'avg_buy': row[9],
            'amount': row[10]
        }
    
    return result


def get_max_loss_record():
    """Zeigt den größten Verlust den du jemals hattest (Gesamt + pro Coin)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Gesamtportfolio - tiefster Punkt
    cursor.execute('''
        SELECT max_loss_eur, max_loss_percent, timestamp_hour, btc_price, xrp_price, eth_price, sol_price
        FROM max_loss_record
        ORDER BY max_loss_eur ASC
        LIMIT 1
    ''')
    total_record = cursor.fetchone()
    
    # Coin-spezifische Max/Min (aus coin_max_min_prices)
    cursor.execute('''
        SELECT coin, max_price_since_buy, max_price_timestamp, max_profit_eur, max_profit_percent,
               min_price_since_buy, min_price_timestamp, min_profit_eur, min_profit_percent,
               avg_buy_price, amount
        FROM coin_max_min_prices
        ORDER BY coin
    ''')
    coin_records = cursor.fetchall()
    
    conn.close()
    
    result = {
        'total': None,
        'coins': {}
    }
    
    if total_record:
        result['total'] = {
            'max_loss': total_record[0],
            'max_loss_percent': total_record[1],
            'timestamp': total_record[2],
            'prices': {'BTC': total_record[3], 'XRP': total_record[4], 'ETH': total_record[5], 'SOL': total_record[6]}
        }
    
    for row in coin_records:
        coin = row[0]
        result['coins'][coin] = {
            'max_price': row[1],
            'max_timestamp': row[2],
            'max_profit_eur': row[3],
            'max_profit_pct': row[4],
            'min_price': row[5],
            'min_timestamp': row[6],
            'min_profit_eur': row[7],
            'min_profit_pct': row[8],
            'avg_buy': row[9],
            'amount': row[10]
        }
    
    return result


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
    
    # Keine Alert bei neuem Rekord - nur speichern!
    # Der Höchstgewinn wird in save_hourly_snapshot() gespeichert,
    # aber es wird KEINE Benachrichtigung ausgelöst.
    
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
    parser.add_argument('--max-verlust', action='store_true', dest='max_verlust', help='Größten Verlust anzeigen')
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
    
    elif args.daily:
        # Daily Report mit aktuellem Status
        import json
        import urllib.request
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Aktuelle Preise für ALLE 4 Coins
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ripple,ethereum,solana&vs_currencies=eur'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            prices = json.loads(response.read().decode())
        
        btc_price = prices['bitcoin']['eur']
        xrp_price = prices['ripple']['eur']
        eth_price = prices['ethereum']['eur']
        sol_price = prices['solana']['eur']
        
        # Holdings laden
        cursor.execute('SELECT coin, amount, invested_eur, avg_buy_price FROM holdings')
        holdings = cursor.fetchall()
        
        total_invested = 0
        total_value = 0
        
        lines = []
        lines.append("📊 **DAILY CRYPTO REPORT**")
        lines.append(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        lines.append("")
        lines.append("💰 Aktuelle Preise:")
        lines.append(f"   BTC: {btc_price:,.2f} €")
        lines.append(f"   XRP: {xrp_price:.4f} €")
        lines.append(f"   ETH: {eth_price:,.2f} €")
        lines.append(f"   SOL: {sol_price:.2f} €")
        lines.append("")
        
        for row in holdings:
            coin, amount, invested, avg_price = row
            if coin == 'BTC':
                current = btc_price * amount
            elif coin == 'XRP':
                current = xrp_price * amount
            elif coin == 'ETH':
                current = eth_price * amount
            elif coin == 'SOL':
                current = sol_price * amount
            else:
                current = invested
            
            profit = current - invested
            profit_pct = (profit / invested * 100) if invested > 0 else 0
            
            # Ampel-Visualisierung für jeden Coin
            if profit > 0:
                ampel = "🟢"
            else:
                ampel = "🔴"
            
            lines.append(f"🪙 **{coin}:**")
            lines.append(f"   Bestand: {amount:.8f}")
            lines.append(f"   Investiert: {invested:.2f} €")
            lines.append(f"   Ø Kaufpreis: {avg_price:,.2f} €")
            lines.append(f"   Wert: {current:.2f} €")
            lines.append(f"   {ampel} P/L: {profit:+.2f} € ({profit_pct:+.2f}%)")
            lines.append("")
            
            total_invested += invested
            total_value += current
        
        total_profit = total_value - total_invested
        total_profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0
        
        # Ampel für Gesamtwert
        if total_profit > 0:
            total_ampel = "🟢"
        else:
            total_ampel = "🔴"
        
        lines.append("=" * 50)
        lines.append(f"💰 **GESAMT:**")
        lines.append(f"   Investiert: {total_invested:.2f} €")
        lines.append(f"   Aktueller Wert: {total_value:.2f} €")
        lines.append(f"   {total_ampel} **Gewinn/Verlust: {total_profit:+.2f} € ({total_profit_pct:+.2f}%)")
        
        conn.close()
        
        report = '\n'.join(lines)
        print(report)
        return 0
    
    elif args.weekly:
        # WÖCHENTLICHER REPORT - Gewinn seit Kauf + Vergleich zur Vorwoche
        import json
        import urllib.request
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        # Aktuelle Preise
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ripple,ethereum,solana&vs_currencies=eur'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            prices = json.loads(response.read().decode())
        
        btc_price = prices['bitcoin']['eur']
        xrp_price = prices['ripple']['eur']
        eth_price = prices['ethereum']['eur']
        sol_price = prices['solana']['eur']
        
        # Aktuelle Holdings
        cursor.execute('SELECT coin, amount, invested_eur, avg_buy_price, first_buy_date FROM holdings')
        holdings = cursor.fetchall()
        
        lines = []
        lines.append("📊 **WÖCHENTLICHER CRYPTO REPORT**")
        lines.append(f"📅 {now.strftime('%d.%m.%Y %H:%M')}")
        lines.append("")
        lines.append("=" * 55)
        lines.append("📈 GEWINN/VERLUST SEIT KAUF")
        lines.append("=" * 55)
        lines.append("")
        
        total_invested = 0
        total_value = 0
        
        # Pro Coin seit Kauf
        for row in holdings:
            coin, amount, invested, avg_price, first_buy = row
            if amount <= 0:
                continue
                
            if coin == 'BTC':
                current = btc_price * amount
            elif coin == 'XRP':
                current = xrp_price * amount
            elif coin == 'ETH':
                current = eth_price * amount
            elif coin == 'SOL':
                current = sol_price * amount
            else:
                current = invested
            
            profit = current - invested
            profit_pct = (profit / invested * 100) if invested > 0 else 0
            
            lines.append(f"🪙 **{coin}** (gekauft: {first_buy or 'unbekannt'})")
            lines.append(f"   Investiert: {invested:.2f} €")
            lines.append(f"   Aktueller Wert: {current:.2f} €")
            lines.append(f"   **Gewinn/Verlust: {profit:+.2f} € ({profit_pct:+.2f}%)**")
            lines.append("")
            
            total_invested += invested
            total_value += current
        
        total_profit = total_value - total_invested
        total_profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0
        
        lines.append("─" * 55)
        lines.append(f"💰 **GESAMT SEIT KAUF:**")
        lines.append(f"   Investiert: {total_invested:.2f} €")
        lines.append(f"   Aktueller Wert: {total_value:.2f} €")
        lines.append(f"   **Gewinn/Verlust: {total_profit:+.2f} € ({total_profit_pct:+.2f}%)**")
        lines.append("")
        
        # VERGLEICH ZUR VORWOCHE (7 Tage)
        lines.append("=" * 55)
        lines.append("📊 VERGLEICH ZUR VORWOCHE (7 Tage)")
        lines.append("=" * 55)
        lines.append("")
        
        # Snapshot von vor einer Woche holen (nur Gesamtwert)
        cursor.execute('''
            SELECT total_value_eur FROM hourly_snapshots 
            WHERE timestamp_hour <= ? 
            ORDER BY timestamp_hour DESC LIMIT 1
        ''', (week_ago.strftime('%Y-%m-%d %H:00'),))
        week_old_row = cursor.fetchone()
        
        if week_old_row:
            week_ago_total = week_old_row[0]
            weekly_change = total_value - week_ago_total
            weekly_change_pct = (weekly_change / week_ago_total * 100) if week_ago_total > 0 else 0
            
            lines.append(f"📅 Vor einer Woche: {week_ago_total:.2f} €")
            lines.append(f"📅 Heute: {total_value:.2f} €")
            lines.append(f"📈 **Änderung: {weekly_change:+.2f} € ({weekly_change_pct:+.2f}%)**")
            
            if weekly_change > 0:
                lines.append("🟢 Diese Woche im Plus!")
            elif weekly_change < 0:
                lines.append("🔴 Diese Woche im Minus")
            else:
                lines.append("⚪ Keine Veränderung")
        else:
            lines.append("⚠️ Keine Daten von vor einer Woche vorhanden")
            lines.append("   (Erst nach nächstem --hourly verfügbar)")
        
        lines.append("")
        lines.append("=" * 55)
        
        conn.close()
        
        report = '\n'.join(lines)
        print(report)
        return 0
    
    elif args.max_profit:
        record = get_max_profit_record()
        if record:
            # Gesamtportfolio
            if record.get('total'):
                print(f"\n🏆 GESAMTPORTFOLIO - Höchster Gewinn:")
                print(f"   💰 Gewinn: {record['total']['max_profit']:+.2f}€ ({record['total']['max_percent']:+.2f}%)")
                print(f"   📅 Zeitpunkt: {record['total']['timestamp']}")
            
            # Pro Coin
            print(f"\n📊 PRO COIN - Max/Min seit Kauf:")
            print("─" * 65)
            for coin, data in record['coins'].items():
                print(f"\n🪙 {coin}")
                print(f"   Ø Kaufpreis: {data['avg_buy']:,.2f}€")
                print(f"   📈 MAX: {data['max_price']:,.2f}€ @ {data['max_timestamp']}")
                print(f"      Gewinn: {data['max_profit_eur']:+.2f}€ ({data['max_profit_pct']:+.2f}%)")
                print(f"   📉 MIN: {data['min_price']:,.2f}€ @ {data['min_timestamp']}")
                print(f"      Verlust: {data['min_profit_eur']:+.2f}€ ({data['min_profit_pct']:+.2f}%)")
                print(f"   💰 Range: {data['min_profit_eur']:+.2f}€ bis {data['max_profit_eur']:+.2f}€")
            
            print(f"\n📈 Letzte Stunden (Gesamt):")
            print("─" * 65)
            for snap in record['recent_snapshots']:
                print(f"   {snap[0]}: {snap[2]:+.2f}€ ({snap[3]:+.2f}%)")
        else:
            print("❌ Noch keine Daten vorhanden. Führe zuerst --hourly aus.")
        return 0
    
    elif args.max_verlust:
        record = get_max_loss_record()
        if record:
            # Gesamtportfolio - tiefster Punkt
            if record.get('total'):
                print(f"\n🔴 GESAMTPORTFOLIO - Größter Verlust:")
                print(f"   💸 Verlust: {record['total']['max_loss']:+.2f}€ ({record['total']['max_loss_percent']:+.2f}%)")
                print(f"   📅 Zeitpunkt: {record['total']['timestamp']}")
            
            # Pro Coin
            print(f"\n📊 PRO COIN - Tiefste Punkte seit Kauf:")
            print("─" * 65)
            for coin, data in record['coins'].items():
                print(f"\n🪙 {coin}")
                print(f"   Ø Kaufpreis: {data['avg_buy']:,.2f}€")
                print(f"   📉 Tiefster Stand: {data['min_price']:,.2f}€ @ {data['min_timestamp']}")
                print(f"      Verlust: {data['min_profit_eur']:+.2f}€ ({data['min_profit_pct']:+.2f}%)")
                print(f"   📈 Höchster Stand: {data['max_price']:,.2f}€ @ {data['max_timestamp']}")
                print(f"      Gewinn: {data['max_profit_eur']:+.2f}€ ({data['max_profit_pct']:+.2f}%)")
                print(f"   💰 Schwankung: {data['min_profit_eur']:+.2f}€ bis {data['max_profit_eur']:+.2f}€")
        else:
            print("❌ Noch keine Daten vorhanden. Führe zuerst --hourly aus.")
        return 0
    
    else:
        print("Verwendung: bison_tracker.py [--init|--hourly|--max-profit|--max-verlust|--buy COIN --amount X --eur Y]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
