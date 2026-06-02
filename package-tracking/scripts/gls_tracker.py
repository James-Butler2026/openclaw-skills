#!/usr/bin/env python3
"""
GLS Sendungsverfolgung – Pragmatisch
1. REST API (gls-group.eu) – funktioniert für 14-stellige GLS-Nummern
2. Link-Ausgabe – wenn API nicht klappt (kurze Nummern)
Kein Browser, kein OCR, kein Cloudflare-Ärger
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'packages.db'

GLS_API_URL = "https://gls-group.eu/app/service/search/rest/de/de/routing/parcel"


def update_db_delivered(tracking_code: str) -> bool:
    """Markiert Paket als delivered in der DB"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE packages SET status='delivered', delivered=1, delivered_at=?, updated_at=? WHERE tracking_code=?",
            (datetime.now().isoformat(), datetime.now().isoformat(), tracking_code)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()


def extract_tracking_code(raw: str) -> str:
    """Extrahiert Tracking-Nummer aus beliebigem Input"""
    raw = raw.strip()
    if 'trackingNumber=' in raw:
        m = re.search(r'trackingNumber=([A-Za-z0-9]+)', raw)
        if m:
            return m.group(1)
    m = re.search(r'(\d{8,20})', raw)
    if m:
        return m.group(1)
    return re.sub(r'[^A-Za-z0-9]', '', raw)


def extract_postcode(raw: str) -> str:
    """Extrahiert PLZ aus URL oder Input"""
    m = re.search(r'post[Cc]ode=(\d{4,5})', raw)
    if m:
        return m.group(1)
    parts = re.split(r'[/#?&=]', raw)
    for i, part in enumerate(parts):
        if part.lower() in ('postcode', 'postalcode', 'plz'):
            if i + 1 < len(parts):
                return parts[i + 1]
    return ''


def normalize_status(status_text: str) -> str:
    """Normalisiert GLS-Status"""
    t = status_text.lower()
    if any(w in t for w in ['zugestellt', 'delivered', 'delivery_ok']):
        return 'delivered'
    if any(w in t for w in ['zustellfahrzeug', 'out_for_delivery', 'on delivery']):
        return 'in_delivery'
    if any(w in t for w in ['paketzentrum', 'in_transit', 'transit', 'sortiert']):
        return 'in_transit'
    if any(w in t for w in ['übernommen', 'abgeholt', 'picked_up']):
        return 'picked_up'
    if any(w in t for w in ['bereitgestellt', 'angekündigt', 'announced', 'erfasst']):
        return 'announced'
    return 'unknown'


def track_gls(tracking_code: str, post_code: str = '') -> dict:
    """Trackt GLS-Paket via REST API mit Fallback auf Link"""
    code = extract_tracking_code(tracking_code)
    plz = post_code or extract_postcode(tracking_code)

    tracking_url = f"https://www.gls-pakete.de/reach-sendungsverfolgung?trackingNumber={code}&postCode={plz}"

    # 1. REST API versuchen (funktioniert für 14-stellige Nummern)
    if plz:
        api_url = f"{GLS_API_URL}?search={code}&postCode={plz}"
    else:
        api_url = f"{GLS_API_URL}?search={code}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'de-DE,de;q=0.9',
        'Referer': 'https://www.gls-pakete.de/reach-sendungsverfolgung',
    }

    req = urllib.request.Request(api_url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read())

            if data.get('exceptionText'):
                err = data.get('exceptionText', '')
                if 'internal system error' in err.lower():
                    # API kennt die Nummer nicht → Link ausgeben
                    return {
                        'success': False,
                        'tracking_code': code,
                        'message': 'GLS API kennt diese Nummer nicht (evtl. zu kurz).',
                        'tracking_url': tracking_url,
                        'api_error': True,
                    }
                return {
                    'success': False,
                    'tracking_code': code,
                    'message': err,
                    'tracking_url': tracking_url,
                }

            parcels = data.get('parcels', data.get('shipments', []))
            if not parcels:
                return {
                    'success': False,
                    'tracking_code': code,
                    'message': 'Keine Sendungsdaten gefunden.',
                    'tracking_url': tracking_url,
                }

            parcel = parcels[0] if isinstance(parcels, list) else parcels

            status_raw = (
                parcel.get('statusText')
                or parcel.get('status')
                or parcel.get('statusDescription')
                or 'Unbekannt'
            )

            status_code = normalize_status(status_raw)

            events = []
            raw_events = (
                parcel.get('events')
                or parcel.get('history')
                or parcel.get('statusEvents')
                or []
            )
            if isinstance(raw_events, list):
                for evt in raw_events:
                    events.append({
                        'date': evt.get('dateTime', evt.get('date', evt.get('timestamp', ''))),
                        'location': evt.get('location', evt.get('city', '')),
                        'status': evt.get('status', evt.get('description', evt.get('text', ''))),
                    })

            # DB-Update bei Zustellung
            if status_code == 'delivered':
                update_db_delivered(code)

            return {
                'success': True,
                'tracking_code': code,
                'carrier': 'gls',
                'status': status_code,
                'status_description': status_raw,
                'events': events,
                'timestamp': datetime.now().isoformat(),
                'tracking_url': tracking_url,
            }

    except urllib.error.HTTPError as e:
        if e.code == 500:
            return {
                'success': False,
                'tracking_code': code,
                'message': 'GLS API kennt diese Nummer nicht (evtl. zu kurz).',
                'tracking_url': tracking_url,
                'api_error': True,
            }
        return {
            'success': False,
            'tracking_code': code,
            'message': f'HTTP Fehler {e.code}',
            'tracking_url': tracking_url,
        }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'tracking_code': code,
            'message': f'Verbindungsfehler: {e.reason}',
            'tracking_url': tracking_url,
        }
    except Exception as e:
        return {
            'success': False,
            'tracking_code': code,
            'message': str(e),
            'tracking_url': tracking_url,
        }


def main():
    parser = argparse.ArgumentParser(description='GLS Sendungsverfolgung (API + Link)')
    parser.add_argument('tracking_code', help='GLS Tracking-Nummer oder URL')
    parser.add_argument('--postal', '-p', default='', help='Postleitzahl')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    args = parser.parse_args()

    result = track_gls(args.tracking_code, args.postal)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if not result.get('success'):
        print("=" * 60)
        print("📦 GLS SENDUNGSSTATUS")
        print("=" * 60)
        print(f"\n❌ {result['message']}")
        print(f"\n🔗 Zum Selbst-Checken (Cloudflare):")
        print(f"   {result['tracking_url']}")
        print("=" * 60)
        sys.exit(1)

    # Erfolg
    icon = {
        'delivered': '✅', 'in_delivery': '🚚', 'in_transit': '📦',
        'picked_up': '📤', 'in_store': '🏪', 'announced': '📋',
        'exception': '⚠️',
    }.get(result['status'], '📦')

    print("=" * 60)
    print(f"{icon} GLS SENDUNGSSTATUS")
    print(f"📦 {result['tracking_code']}")
    print("=" * 60)
    print(f"\n✅ Status: {result['status_description']}")
    print(f"   Code: {result['status']}")

    if result.get('events'):
        print(f"\n📋 Letzte Updates:")
        for evt in result['events'][:5]:
            d = evt['date'][:16] if evt['date'] else ''
            s = evt['status'][:60] if evt['status'] else ''
            l = f" ({evt['location']})" if evt.get('location') else ''
            print(f"   • {d}{l}: {s}")

    print(f"\n🔗 Tracking: {result['tracking_url']}")
    print("=" * 60)


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result.get('success') else 1)