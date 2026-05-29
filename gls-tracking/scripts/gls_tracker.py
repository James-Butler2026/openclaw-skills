#!/usr/bin/env python3
"""
GLS Sendungsverfolgung via gls-group.eu (OHNE API-Key!)
Nutzt den öffentlichen REST-Endpoint von GLS
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime

GLS_URL = "https://gls-group.eu/app/service/search/rest/de/de/routing/parcel"

def extract_tracking_code(raw: str) -> str:
    """Extrahiert Tracking-Nummer aus beliebigem Input (URL, Nummer, etc.)"""
    raw = raw.strip()
    # URL? Letzten Teil nach / oder # extrahieren
    if '/' in raw or '#' in raw:
        # Letzten alphanumerischen Block
        parts = re.split(r'[/#?&=]', raw)
        for part in reversed(parts):
            part = part.strip()
            if re.match(r'^[A-Za-z0-9]{8,20}$', part):
                return part
    # Sonst nur Ziffern/Buchstaben
    code = re.sub(r'[^A-Za-z0-9]', '', raw)
    return code

def validate_tracking_code(code: str) -> tuple:
    """Validiert GLS Tracking-Nummer und gibt (gültig, format_name) zurück"""
    if re.match(r'^\d{14}$', code):
        return True, '14-digit'
    if re.match(r'^\d{12,16}$', code):
        return True, 'numeric'
    if re.match(r'^[A-Z0-9]{8,12}$', code):
        return True, 'alphanumeric'
    if re.match(r'^[A-Z]{2}\d{9}[A-Z]{2}$', code):
        return True, 'international'
    return False, 'unknown'

def track_gls(tracking_code: str) -> dict:
    """Trackt GLS-Paket ohne API-Key via öffentlichem REST-Endpoint"""
    code = extract_tracking_code(tracking_code)
    is_valid, fmt = validate_tracking_code(code)
    
    url = f"{GLS_URL}?search={code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'de-DE,de;q=0.9',
        'Referer': 'https://gls-group.com/DE/de/parcel-tracking',
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            
            # Fehler vom Server
            if data.get('exceptionText') or data.get('lastError'):
                err_msg = data.get('exceptionText', data.get('lastError', 'Unbekannter Fehler'))
                # 500 bei ungültiger Nummer ist normal
                if 'internal system error' in err_msg.lower() or 'try again later' in err_msg.lower():
                    return {
                        'error': True,
                        'message': 'Ungültige oder unbekannte GLS Tracking-Nummer'
                    }
                return {'error': True, 'message': err_msg}
            
            # Erfolgreiche Response parsen
            parcels = data.get('parcels', data.get('shipments', []))
            if not parcels:
                return {'error': True, 'message': 'Keine Sendungsdaten gefunden'}
            
            parcel = parcels[0] if isinstance(parcels, list) else parcels
            
            # Verschiedene Response-Strukturen
            status_raw = (
                parcel.get('statusText') or
                parcel.get('status') or
                parcel.get('statusDescription') or
                'Unbekannt'
            )
            
            status_code_raw = (
                parcel.get('statusCode') or
                parcel.get('status_code') or
                ''
            )
            
            status_code = normalize_status(status_raw, status_code_raw)
            
            # Events/History
            events = []
            raw_events = (
                parcel.get('events') or
                parcel.get('history') or
                parcel.get('statusEvents') or
                []
            )
            if isinstance(raw_events, list):
                for evt in raw_events:
                    events.append({
                        'datum': evt.get('dateTime', evt.get('date', evt.get('timestamp', ''))),
                        'ort': evt.get('location', evt.get('city', '')),
                        'status': evt.get('status', evt.get('description', evt.get('text', ''))),
                    })
            
            estimated_delivery = (
                parcel.get('estimatedDeliveryDate') or
                parcel.get('deliveryDate') or
                parcel.get('expectedDelivery') or
                None
            )
            
            return {
                'tracking_code': code,
                'carrier': 'gls',
                'status': status_code,
                'status_description': status_raw,
                'timestamp': datetime.now().isoformat(),
                'events': events,
                'estimated_delivery': estimated_delivery,
                'raw_response': data,  # Für Debugging
            }
            
    except urllib.error.HTTPError as e:
        if e.code == 500:
            return {'error': True, 'message': 'Ungültige oder unbekannte GLS Tracking-Nummer'}
        return {'error': True, 'message': f'HTTP Fehler {e.code}'}
    except urllib.error.URLError as e:
        return {'error': True, 'message': f'Verbindungsfehler: {e.reason}'}
    except json.JSONDecodeError:
        return {'error': True, 'message': 'Ungültige Antwort vom GLS-Server'}
    except Exception as e:
        return {'error': True, 'message': str(e)}

def normalize_status(status_text: str, status_code: str = '') -> str:
    """Normalisiert GLS-Status auf gemeinsame Codes"""
    t = (status_text + ' ' + status_code).lower()
    
    if any(w in t for w in ['delivered', 'zugestellt', 'delivery_ok']):
        return 'delivered'
    if any(w in t for w in ['out_for_delivery', 'in_delivery', 'zustellfahrzeug', 'on delivery']):
        return 'in_delivery'
    if any(w in t for w in ['in_transit', 'transit', 'parcel center', 'paketzentrum', 'sorting', 'sortiert']):
        return 'in_transit'
    if any(w in t for w in ['picked_up', 'collected', 'abgeholt']):
        return 'picked_up'
    if any(w in t for w in ['parcel_shop', 'filiale', 'parcel shop', 'bereit']):
        return 'in_store'
    if any(w in t for w in ['announced', 'angekündigt', 'electronic', 'elektronisch']):
        return 'announced'
    if any(w in t for w in ['exception', 'problem', 'delay', 'verzögerung', 'error']):
        return 'exception'
    
    return 'unknown'

def main():
    parser = argparse.ArgumentParser(description='GLS Sendungsverfolgung (ohne API-Key)')
    parser.add_argument('tracking_code', help='GLS Tracking-Nummer oder URL')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Nur Ergebnisse')
    
    args = parser.parse_args()
    
    result = track_gls(args.tracking_code)
    
    if result.get('error'):
        if args.json:
            print(json.dumps(result))
        else:
            print(f"❌ {result['message']}")
        sys.exit(1)
    
    if args.json:
        # Ohne raw_response für sauberen Output
        clean = {k: v for k, v in result.items() if k != 'raw_response'}
        print(json.dumps(clean, indent=2, ensure_ascii=False))
    elif not args.quiet:
        status_icon = {
            'delivered': '✅',
            'in_delivery': '🚚',
            'in_transit': '📦',
            'picked_up': '📤',
            'in_store': '🏪',
            'announced': '📋',
            'exception': '⚠️',
        }.get(result['status'], '📦')
        
        print("=" * 60)
        print(f"{status_icon} GLS SENDUNGSSTATUS")
        print(f"📦 {result['tracking_code']}")
        print("=" * 60)
        print(f"\n✅ Status: {result['status_description']}")
        print(f"   Code: {result['status']}")
        if result.get('estimated_delivery'):
            print(f"📅 Voraussichtliche Zustellung: {result['estimated_delivery']}")
        if result.get('events'):
            print(f"\n📋 Letzte Updates:")
            for evt in result['events'][:5]:
                datum = evt['datum'][:16] if evt['datum'] else 'Unbekannt'
                ort = f" ({evt['ort']})" if evt.get('ort') else ''
                status_text = evt['status'][:60] if evt['status'] else ''
                print(f"   • {datum}{ort}: {status_text}")
        print("=" * 60)
    
    return result

if __name__ == '__main__':
    result = main()
    sys.exit(0 if not result.get('error') else 1)
