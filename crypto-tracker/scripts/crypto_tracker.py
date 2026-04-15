#!/usr/bin/env python3
"""
Crypto Portfolio Tracker - Erweiterte Version
Trackt BTC/XRP Investments mit Gewinn/Verlust-Berechnung, Stop-Loss, Performance-Vergleich, Trade-Historie, Durchschnittskosten
"""

import sqlite3
import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "crypto_portfolio.db"
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


def get_portfolio_status(check_alerts=True):
    """Zeigt aktuellen Portfolio-Status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT coin, amount, invested_eur, avg_buy_price, first_buy_date, last_buy_date FROM holdings')
    holdings = cursor.fetchall()
    conn.close()
    
    if not holdings:
        print("❌ Keine Bestände gefunden. Führe --init aus.")
        return None
    
    prices = get_crypto_prices()
    if not prices:
        return None
    
    results = []
    total_invested = 0
    total_current = 0
    
    alerts = []
    
    print(f"\n💰 Bison Portfolio Status ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n")
    print("─" * 65)
    
    for coin, amount, invested, avg_price, first_buy, last_buy in holdings:
        # Coin ID Mapping für CoinGecko
        coin_map = {
            'BTC': 'bitcoin',
            'XRP': 'ripple', 
            'ETH': 'ethereum',
            'SOL': 'solana'
        }
        coin_id = coin_map.get(coin, coin.lower())
        price_data = prices.get(coin_id, {})
        
        current_price_eur = price_data.get('eur', 0)
        current_price_usd = price_data.get('usd', 0)
        current_value = amount * current_price_eur
        profit_loss = current_value - invested
        profit_percent = ((current_value - invested) / invested) * 100 if invested > 0 else 0
        
        # Performance vs Durchschnittskaufpreis
        performance_vs_avg = ((current_price_eur - avg_price) / avg_price) * 100 if avg_price > 0 else 0
        
        total_invested += invested
        total_current += current_value
        
        # Stop-Loss Check
        if profit_percent <= STOP_LOSS_PERCENT:
            alerts.append(f"🚨 STOP-LOSS WARNUNG: {coin} ist bei {profit_percent:.1f}%!")
        
        emoji = "🟢" if profit_loss >= 0 else "🔴"
        vs_avg_emoji = "🟢" if performance_vs_avg >= 0 else "🔴"
        
        print(f"\n🪙 {coin}")
        print(f"   📊 Bestand: {amount:,.8f} {coin}")
        print(f"   💶 Investiert: {invested:.2f}€")
        print(f"   📈 Aktueller Wert: {current_value:.2f}€")
        print(f"   💰 Ø Kaufpreis: {avg_price:,.2f}€")
        print(f"   📊 Aktueller Kurs: {current_price_eur:,.2f}€")
        print(f"   {emoji} G/V: {profit_loss:+.2f}€ ({profit_percent:+.2f}%)")
        print(f"   {vs_avg_emoji} vs Ø-Kauf: {performance_vs_avg:+.2f}%")
        print(f"   📅 Erster Kauf: {first_buy[:10] if first_buy else 'N/A'}")
        
        results.append({
            'coin': coin,
            'amount': amount,
            'invested': invested,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'profit_percent': profit_percent,
            'avg_buy_price': avg_price,
            'price_eur': current_price_eur,
            'price_usd': current_price_usd,
            'performance_vs_avg': performance_vs_avg
        })
    
    # Performance-Vergleich
    print("\n" + "─" * 65)
    print(f"\n🏆 Performance-Vergleich:")
    
    if len(results) >= 2:
        best = max(results, key=lambda x: x['profit_percent'])
        worst = min(results, key=lambda x: x['profit_percent'])
        print(f"   🥇 Beste Performance: {best['coin']} ({best['profit_percent']:+.2f}%)")
        print(f"   🥉 Schlechteste Performance: {worst['coin']} ({worst['profit_percent']:+.2f}%)")
    
    total_profit = total_current - total_invested
    total_percent = ((total_current - total_invested) / total_invested) * 100 if total_invested > 0 else 0
    total_emoji = "🟢" if total_profit >= 0 else "🔴"
    
    print("\n" + "─" * 65)
    print(f"\n📊 GESAMT PORTFOLIO")
    print(f"   💶 Investiert: {total_invested:.2f}€")
    print(f"   📈 Aktueller Wert: {total_current:.2f}€")
    print(f"   {total_emoji} Gewinn/Verlust: {total_profit:+.2f}€ ({total_percent:+.2f}%)")
    print("\n" + "─" * 65)
    
    # Alerts anzeigen
    if alerts:
        print("\n⚠️ ALERTS:")
        for alert in alerts:
            print(f"   {alert}")
        print("─" * 65)
    
    return {
        'holdings': results,
        'total_invested': total_invested,
        'total_current': total_current,
        'total_profit': total_profit,
        'total_percent': total_percent,
        'alerts': alerts
    }


def get_trade_history(coin=None, limit=20):
    """Zeigt Trade-Historie"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if coin:
        cursor.execute('''
            SELECT coin, type, amount, price_eur, total_eur, timestamp 
            FROM trades 
            WHERE coin = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (coin, limit))
    else:
        cursor.execute('''
            SELECT coin, type, amount, price_eur, total_eur, timestamp 
            FROM trades 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
    
    trades = cursor.fetchall()
    conn.close()
    
    print(f"\n📜 Trade-Historie{' (' + coin + ')' if coin else ''}\n")
    print("─" * 65)
    
    if not trades:
        print("   Keine Trades gefunden")
        return
    
    for coin, type, amount, price, total, timestamp in trades:
        emoji = "🟢" if type == 'buy' else "🔴"
        print(f"   {emoji} {timestamp[:16]} | {type.upper():4} | {amount:,.8f} {coin} @ {price:,.2f}€ = {total:.2f}€")
    
    print("─" * 65)


def get_performance_comparison():
    """Vergleicht Performance der Coins"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT coin, invested_eur, avg_buy_price 
        FROM holdings
    ''')
    holdings = cursor.fetchall()
    conn.close()
    
    prices = get_crypto_prices()
    if not prices:
        return
    
    print(f"\n🏆 Performance-Vergleich ({datetime.now().strftime('%d.%m.%Y')})\n")
    print("─" * 65)
    
    performances = []
    coin_map = {
        'BTC': 'bitcoin',
        'XRP': 'ripple',
        'ETH': 'ethereum',
        'SOL': 'solana'
    }
    
    for coin, invested, avg_price in holdings:
        coin_id = coin_map.get(coin, coin.lower())
        current_price = prices.get(coin_id, {}).get('eur', 0)
        performance = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
        performances.append((coin, performance, current_price, avg_price))
    
    # Sortiere nach Performance
    performances.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (coin, perf, current, avg) in enumerate(performances, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "4️⃣"
        emoji = "🟢" if perf >= 0 else "🔴"
        print(f"\n   {medal} #{rank} {coin}")
        print(f"      {emoji} Performance: {perf:+.2f}%")
        print(f"      💰 Ø Kauf: {avg:,.2f}€ → Aktuell: {current:,.2f}€")
    
    print("\n" + "─" * 65)


def save_daily_snapshot():
    """Speichert täglichen Snapshot"""
    status = get_portfolio_status(check_alerts=False)
    if not status:
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for holding in status['holdings']:
        cursor.execute('''
            INSERT INTO daily_snapshots 
            (coin, amount, price_usd, price_eur, value_eur, profit_loss_eur, profit_loss_percent, snapshot_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            holding['coin'],
            holding['amount'],
            holding['price_usd'],
            holding['price_eur'],
            holding['current_value'],
            holding['profit_loss'],
            holding['profit_percent'],
            today
        ))
    
    conn.commit()
    conn.close()
    print(f"\n💾 Snapshot für {today} gespeichert")


def get_weekly_report():
    """Erstellt Wochenbericht"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Heutige Daten
    cursor.execute('''
        SELECT coin, value_eur, profit_loss_eur, profit_loss_percent
        FROM daily_snapshots
        WHERE date(snapshot_date) = date('now')
        ORDER BY snapshot_date DESC
    ''')
    today_data = {row[0]: row for row in cursor.fetchall()}
    
    # Vor 7 Tagen
    cursor.execute('''
        SELECT coin, value_eur, profit_loss_eur, profit_loss_percent
        FROM daily_snapshots
        WHERE date(snapshot_date) = date('now', '-7 days')
        ORDER BY snapshot_date DESC
    ''')
    week_ago_data = {row[0]: row for row in cursor.fetchall()}
    
    conn.close()
    
    print(f"\n📈 Wochenbericht ({datetime.now().strftime('%d.%m.%Y')})\n")
    print("─" * 65)
    
    if not today_data:
        print("❌ Keine aktuellen Daten vorhanden")
        return
    
    total_today_value = 0
    total_week_ago_value = 0
    
    for coin in today_data:
        today_row = today_data[coin]
        _, today_value, today_profit, today_percent = today_row
        total_today_value += today_value
        
        print(f"\n🪙 {coin}")
        print(f"   💶 Aktueller Wert: {today_value:.2f}€")
        print(f"   {'🟢' if today_profit >= 0 else '🔴'} Gesamt-G/V: {today_profit:+.2f}€ ({today_percent:+.2f}%)")
        
        if coin in week_ago_data:
            _, week_ago_value, week_ago_profit, week_ago_percent = week_ago_data[coin]
            total_week_ago_value += week_ago_value
            week_change = today_value - week_ago_value
            week_change_percent = (week_change / week_ago_value) * 100 if week_ago_value > 0 else 0
            week_emoji = "🟢" if week_change >= 0 else "🔴"
            print(f"   {week_emoji} 7-Tage-Änderung: {week_change:+.2f}€ ({week_change_percent:+.2f}%)")
        else:
            print(f"   ⚪ Keine Daten von vor 7 Tagen")
    
    if total_week_ago_value > 0:
        total_week_change = total_today_value - total_week_ago_value
        total_week_change_percent = (total_week_change / total_week_ago_value) * 100
        total_emoji = "🟢" if total_week_change >= 0 else "🔴"
        
        print("\n" + "─" * 65)
        print(f"\n📊 PORTFOLIO WOChen-VERGLEICH")
        print(f"   Vor 7 Tagen: {total_week_ago_value:.2f}€")
        print(f"   Heute: {total_today_value:.2f}€")
        print(f"   {total_emoji} Änderung: {total_week_change:+.2f}€ ({total_week_change_percent:+.2f}%)")
    
    print("\n" + "─" * 65)


def save_hourly_price(coin, price_eur):
    """Speichert stündlichen Preis für Bewegungs-Erkennung"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabelle für stündliche Preise erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hourly_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            price_eur REAL NOT NULL,
            hour TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO hourly_prices (coin, price_eur) VALUES (?, ?)
    ''', (coin, price_eur))
    
    # Alte Einträge löschen (älter als 48 Stunden)
    cursor.execute('''
        DELETE FROM hourly_prices 
        WHERE hour < datetime('now', '-48 hours')
    ''')
    
    conn.commit()
    conn.close()


def get_last_hour_price(coin):
    """Holt Preis von vor einer Stunde"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT price_eur FROM hourly_prices 
        WHERE coin = ? 
        ORDER BY hour DESC 
        LIMIT 1 OFFSET 0
    ''', (coin,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None


def check_hourly_alerts():
    """Prüft stündlich auf signifikante Preisbewegungen"""
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
        # Coin ID Mapping für CoinGecko
        coin_map = {
            'BTC': 'bitcoin',
            'XRP': 'ripple',
            'ETH': 'ethereum', 
            'SOL': 'solana'
        }
        coin_id = coin_map.get(coin, coin.lower())
        current_price = prices.get(coin_id, {}).get('eur', 0)
        
        # Speichere aktuellen Preis
        save_hourly_price(coin, current_price)
        
        # Berechne Gesamt-Performance
        current_value = amount * current_price
        total_profit_percent = ((current_value - invested) / invested) * 100 if invested > 0 else 0
        
        # Prüfe Stop-Loss
        if total_profit_percent <= STOP_LOSS_PERCENT:
            alerts.append(f"🚨 STOP-LOSS: {coin} bei {total_profit_percent:.1f}%! (Kurs: {current_price:.2f}€)")
        
        # Prüfe Take-Profit
        if total_profit_percent >= TAKE_PROFIT_PERCENT:
            alerts.append(f"🎯 TAKE-PROFIT: {coin} bei +{total_profit_percent:.1f}%! (Kurs: {current_price:.2f}€)")
        
        # Prüfe stündliche Bewegung
        last_price = get_last_hour_price(coin)
        if last_price and last_price > 0:
            hour_change = ((current_price - last_price) / last_price) * 100
            if abs(hour_change) >= HOURLY_ALERT_PERCENT:
                direction = "🟢 +" if hour_change > 0 else "🔴"
                alerts.append(f"{direction} {coin} stündliche Bewegung: {hour_change:+.2f}% ({last_price:.2f}€ → {current_price:.2f}€)")
    
    return alerts


def get_inline_buttons_text():
    """Generiert Text für Telegram Inline-Buttons"""
    return """
🔘 Inline-Buttons verfügbar:
   [🔄 Aktualisieren] [📈 Wochenbericht] [📜 Historie]
   [🏆 Performance] [💰 Status]

Oder Befehle: /crypto_status /crypto_weekly /crypto_history
"""


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto Portfolio Tracker')
    parser.add_argument('--init', action='store_true', help='Datenbank initialisieren')
    parser.add_argument('--status', action='store_true', help='Aktuellen Status anzeigen')
    parser.add_argument('--daily', action='store_true', help='Tägliches Update mit Snapshot')
    parser.add_argument('--weekly', action='store_true', help='Wochenbericht')
    parser.add_argument('--history', action='store_true', help='Trade-Historie anzeigen')
    parser.add_argument('--performance', action='store_true', help='Performance-Vergleich')
    parser.add_argument('--hourly', action='store_true', help='Stündlicher Check mit Alerts')
    parser.add_argument('--buy', metavar='COIN', help='Neuen Kauf hinzufügen (BTC/XRP)')
    parser.add_argument('--amount', type=float, help='Menge')
    parser.add_argument('--eur', type=float, help='Investierter Betrag in EUR')
    parser.add_argument('--coin', help='Coin für Historie')
    parser.add_argument('--json', action='store_true', help='JSON Output')
    parser.add_argument('--buttons', action='store_true', help='Zeigt verfügbare Buttons')
    
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
    
    if args.status:
        result = get_portfolio_status()
        if args.json and result:
            print(json.dumps(result, indent=2))
        return 0 if result else 1
    
    elif args.hourly:
        # Stündlicher Check mit Alert-Erkennung
        alerts = check_hourly_alerts()
        if alerts:
            print("\n⚠️ SIGNIFIKANTE BEWEGUNGEN ERKANNT:\n")
            for alert in alerts:
                print(f"   {alert}")
            print("\n" + "─" * 65)
            return 1  # Return 1 damit Cron merkt dass was wichtiges passiert ist
        else:
            print("✅ Keine signifikanten Bewegungen (±5% oder Stop-Loss/Take-Profit nicht erreicht)")
            return 0
    
    elif args.daily:
        result = get_portfolio_status()
        save_daily_snapshot()
        if result:
            print(get_inline_buttons_text())
        return 0
    
    elif args.weekly:
        get_weekly_report()
        return 0
    
    elif args.history:
        get_trade_history(coin=args.coin)
        return 0
    
    elif args.performance:
        get_performance_comparison()
        return 0
    
    elif args.buttons:
        print(get_inline_buttons_text())
        return 0
    
    else:
        # Default: Status + Buttons
        result = get_portfolio_status()
        if result:
            print(get_inline_buttons_text())
        return 0 if result else 1


if __name__ == '__main__':
    exit(main())
