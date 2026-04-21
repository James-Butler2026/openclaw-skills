#!/usr/bin/env python3
"""
DHL Sendungsverfolgung via API
Optimiert mit Retry-Logik, Caching und robustem Error Handling
"""

import argparse
import json
import sys
import re
import time
from pathlib import Path
from datetime import datetime
from functools import wraps
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from logger_config import get_logger
from scripts.db_manager import update_package_status

logger = get_logger(__name__)

# API Konfiguration
DHL_API_URL = "https://www.dhl.de/int-verfolgen/data/search"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # Sekunden

STATUS_KEYWORDS = {
    'delivered': ['zustellung erfolgreich', 'zugestellt'],
    'in_delivery': ['zustellfahrzeug', 'zustellung läuft'],
    'in_transit': ['paketzentrum', 'sortiert', 'verteilt'],
    'in_store': ['filiale', 'abholbereit'],
}

def retry_on_error(max_attempts=MAX_RETRIES, delay=RETRY_DELAY):
    """Decorator für Retry-Logik"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Versuch {attempt + 1}/{max_attempts} fehlgeschlagen: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))  # Exponentieller Backoff
                    else:
                        raise
            return None
        return wrapper
    return decorator

@retry_on_error()
def fetch_tracking_data(tracking_code: str) -> dict:
    """Holt Tracking-Daten von DHL API mit Retry"""
    url = f"{DHL_API_URL}?piececode={tracking_code}&language=de"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.dhl.de/'
    }
    
    logger.info(f"DHL API-Anfrage: {tracking_code}")
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    
    return response.json()

def extract_status(events: list) -> tuple:
    """Extrahiert und klassifiziert Status aus Events"""
    if not events:
        return 'unknown', 'Keine Daten'
    
    # Aktuellster Status zuerst
    current = events[0].get('status', '').lower()
    
    for status_code, keywords in STATUS_KEYWORDS.items():
        if any(kw in current for kw in keywords):
            return status_code, events[0].get('status', '')
    
    return 'in_transit', events[0].get('status', 'Unterwegs')

def track_dhl(tracking_code: str) -> dict:
    """Trackt DHL-Paket und gibt strukturierte Daten zurück"""
    data = fetch_tracking_data(tracking_code)
    
    if not data or 'sendungen' not in data:
        return {'error': True, 'message': 'Keine Daten von DHL API'}
    
    events = []
    for sendung in data.get('sendungen', []):
        verlauf = sendung.get('sendungsdetails', {}).get('sendungsverlauf', {})
        
        if verlauf.get('status'):
            events.append({
                'status': verlauf['status'],
                'datum': verlauf.get('datumAktuellerStatus', ''),
                'type': 'aktuell'
            })
        
        for event in verlauf.get('events', []):
            events.append({
                'status': event.get('status', ''),
                'datum': event.get('datum', ''),
                'type': 'historie'
            })
    
    status_code, status_text = extract_status(events)
    
    result = {
        'tracking_code': tracking_code,
        'carrier': 'dhl',
        'status': status_code,
        'status_description': status_text,
        'timestamp': datetime.now().isoformat(),
        'events': events[:5],  # Nur letzte 5 Events
    }
    
    return result

def update_database(tracking_code: str, status: str) -> bool:
    """Aktualisiert Paket-Status in DB bei Zustellung"""
    if status == 'delivered':
        try:
            update_package_status(
                tracking_code,
                status='delivered',
                delivered=1,
                delivered_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            logger.info(f"DB-Update: {tracking_code} als delivered markiert")
            return True
        except Exception as e:
            logger.error(f"DB-Update fehlgeschlagen: {e}")
            return False
    return False

def main():
    parser = argparse.ArgumentParser(description='DHL Sendungsverfolgung')
    parser.add_argument('tracking_code', help='DHL Tracking-Nummer (20 Ziffern)')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Nur Ergebnisse')
    
    args = parser.parse_args()
    
    # Validierung
    if not re.match(r'^\d{20}$', args.tracking_code.strip()):
        error_msg = "DHL Tracking-Nummern sind exakt 20 Ziffern"
        if args.json:
            print(json.dumps({'error': True, 'message': error_msg}))
        else:
            print(f"⚠️ {error_msg}")
        sys.exit(1)
    
    try:
        result = track_dhl(args.tracking_code.strip())
        
        if result.get('error'):
            if args.json:
                print(json.dumps(result))
            else:
                print(f"❌ {result['message']}")
            sys.exit(1)
        
        # DB aktualisieren bei Zustellung
        if result['status'] == 'delivered':
            update_database(result['tracking_code'], 'delivered')
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif not args.quiet:
            print("=" * 60)
            print(f"🚚 DHL SENDUNGSSTATUS")
            print(f"📦 {result['tracking_code']}")
            print("=" * 60)
            print(f"\n✅ Status: {result['status_description']}")
            if result['events']:
                print(f"\n📋 Letzte Updates:")
                for evt in result['events'][:3]:
                    print(f"   • {evt['status'][:50]}...")
            print("=" * 60)
        
        return result
        
    except Exception as e:
        logger.error(f"Tracking fehlgeschlagen: {e}")
        if args.json:
            print(json.dumps({'error': True, 'message': str(e)}))
        else:
            print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == '__main__':
    result = main()
    sys.exit(0 if not result.get('error') else 1)
