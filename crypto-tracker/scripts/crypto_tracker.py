#!/usr/bin/env python3
"""
Crypto Tracker - Krypto-Kurse via CoinGecko API
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


def get_prices(coins=None):
    """
    Holt aktuelle Krypto-Preise von CoinGecko API.
    
    Args:
        coins: Liste von Coin-IDs (default: ['bitcoin', 'ripple'])
    
    Returns:
        dict mit Preisen und 24h Änderungen
    """
    if coins is None:
        coins = ['bitcoin', 'ripple']
    
    coin_ids = ','.join(coins)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd,eur&include_24hr_change=true"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data
            
    except urllib.error.HTTPError as e:
        print(f"❌ API Fehler: {e.code}")
        return None
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None


def format_price(value):
    """Formatiert Preis mit passenden Dezimalstellen"""
    if value >= 1000:
        return f"{value:,.0f}"
    elif value >= 1:
        return f"{value:,.2f}"
    else:
        return f"{value:,.4f}"


def format_change(change):
    """Formatiert 24h Änderung mit Emoji"""
    if change > 0:
        return f"🟢 +{change:.2f}%"
    elif change < 0:
        return f"🔴 {change:.2f}%"
    else:
        return "⚪ 0.00%"


def display_prices(data):
    """Zeigt formatierte Preise an"""
    if not data:
        return
    
    print(f"\n💰 Krypto-Kurse ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n")
    print("─" * 50)
    
    coin_names = {
        'bitcoin': 'BTC',
        'ripple': 'XRP',
        'ethereum': 'ETH',
        'solana': 'SOL'
    }
    
    for coin_id, prices in data.items():
        symbol = coin_names.get(coin_id, coin_id.upper())
        usd_price = prices.get('usd', 0)
        eur_price = prices.get('eur', 0)
        usd_change = prices.get('usd_24h_change', 0)
        eur_change = prices.get('eur_24h_change', 0)
        
        print(f"\n🪙 {symbol}")
        print(f"   💵 USD: ${format_price(usd_price)} {format_change(usd_change)}")
        print(f"   💶 EUR: {format_price(eur_price)}€ {format_change(eur_change)}")
    
    print("\n" + "─" * 50)
    print("\n📊 Quelle: CoinGecko API")


def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto Tracker')
    parser.add_argument('--coins', default='bitcoin,ripple', help='Komma-separierte Liste (default: bitcoin,ripple)')
    parser.add_argument('--json', action='store_true', help='JSON Output')
    
    args = parser.parse_args()
    
    coins = [c.strip() for c in args.coins.split(',')]
    data = get_prices(coins)
    
    if data:
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            display_prices(data)
        return 0
    else:
        print("❌ Konnte Kurse nicht abrufen")
        return 1


if __name__ == '__main__':
    exit(main())
