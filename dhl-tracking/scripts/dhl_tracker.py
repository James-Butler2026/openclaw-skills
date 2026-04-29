#!/usr/bin/env python3
"""
DHL Sendungsverfolgung via DHL.de (OHNE API-Key!)
Nutzt die öffentliche internationale Verfolgung von DHL
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

DHL_URL = "https://www.dhl.de/int-verfolgen/data/search"

def track_dhl(tracking_code: str) -> dict:
    """Trackt DHL-Paket ohne API-Key"""
    url = f"{DHL_URL}?piececode={tracking_code}&language=de"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'de-DE,de;q=0.9',
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            
            if 'sendungen' not in data or not data['sendungen']:
                return {'error': True, 'message': 'Keine Sendungsdaten gefunden'}
            
            sendung = data['sendungen'][0]
            details = sendung.get('sendungsdetails', {})
            verlauf = details.get('sendungsverlauf', {})
            
            # Status extrahieren
            status_text = verlauf.get('status', 'Unbekannt')
            status_code = verlauf.get('statusCode', 'unknown')
            fortschritt = verlauf.get('fortschritt', 0)
            max_fortschritt = verlauf.get('maximalFortschritt', 5)
            
            # Events
            events = []
            for event in verlauf.get('events', []):
                events.append({
                    'datum': event.get('datum', ''),
                    'status': event.get('status', '')
                })
            
            # Ist zugestellt?
            ist_zugestellt = details.get('istZugestellt', False)
            
            return {
                'tracking_code': tracking_code,
                'carrier': 'dhl',
                'status': 'delivered' if ist_zugestellt else 'in_transit',
                'status_description': status_text,
                'progress': f"{fortschritt}/{max_fortschritt}",
                'timestamp': datetime.now().isoformat(),
                'events': events,
                'ziel_land': details.get('zielland', 'Deutschland')
            }
            
    except urllib.error.HTTPError as e:
        return {'error': True, 'message': f'HTTP Fehler {e.code}'}
    except Exception as e:
        return {'error': True, 'message': str(e)}

def main():
    parser = argparse.ArgumentParser(description='DHL Sendungsverfolgung (ohne API-Key)')
    parser.add_argument('tracking_code', help='DHL Tracking-Nummer')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Nur Ergebnisse')
    
    args = parser.parse_args()
    
    result = track_dhl(args.tracking_code.strip())
    
    if result.get('error'):
        if args.json:
            print(json.dumps(result))
        else:
            print(f"❌ {result['message']}")
        sys.exit(1)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif not args.quiet:
        print("=" * 60)
        print(f"🚚 DHL SENDUNGSSTATUS")
        print(f"📦 {result['tracking_code']}")
        print("=" * 60)
        print(f"\n✅ Status: {result['status_description']}")
        print(f"📊 Fortschritt: {result['progress']}")
        if result['events']:
            print(f"\n📋 Letzte Updates:")
            for evt in result['events'][:3]:
                datum = evt['datum'][:16] if evt['datum'] else 'Unbekannt'
                print(f"   • {datum}: {evt['status'][:60]}...")
        print("=" * 60)
    
    return result

if __name__ == '__main__':
    result = main()
    sys.exit(0 if not result.get('error') else 1)
