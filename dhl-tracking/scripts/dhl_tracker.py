#!/usr/bin/env python3
"""
DHL Sendungsverfolgung via API
Prüft Tracking-Status via DHL JSON-Endpoint
Überwacht Sendungen um 10:00 und 16:00 Uhr
"""

import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime
import requests

# Zentrales Logging importieren
sys.path.insert(0, '/home/node/.openclaw/workspace/scripts')
from logger_config import get_logger

logger = get_logger(__name__)

# Status-Schlüsselwörter die wir suchen
STATUS_KEYWORDS = [
    "in das zustellfahrzeug geladen",
    "in das Zustellfahrzeug geladen",
    "zustellung erfolgreich",
    "zugestellt",
    "in der filiale",
    "im paketzentrum",
    "briefzentrum bearbeitet",
]

def fetch_tracking_data(tracking_code: str) -> dict:
    """Holt Tracking-Daten von DHL API"""
    url = f"https://www.dhl.de/int-verfolgen/data/search?piececode={tracking_code}&language=de"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.dhl.de/'
    }
    
    try:
        logger.info(f"Frage DHL-Tracking ab: {tracking_code}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.debug(f"DHL-Response erhalten für {tracking_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"DHL API-Fehler: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"DHL JSON-Fehler: {e}")
        return None

def extract_events(data: dict) -> list:
    """Extrahiert alle Events aus DHL-Response"""
    events = []
    
    if not data or 'sendungen' not in data:
        return events
    
    for sendung in data.get('sendungen', []):
        details = sendung.get('sendungsdetails', {})
        verlauf = details.get('sendungsverlauf', {})
        
        # Aktueller Status (oberste Ebene)
        aktueller_status = verlauf.get('status', '')
        if aktueller_status:
            events.append({
                'type': 'aktuell',
                'status': aktueller_status,
                'datum': verlauf.get('datumAktuellerStatus', ''),
                'fortschritt': verlauf.get('fortschritt', 0),
                'max_fortschritt': verlauf.get('maximalFortschritt', 5)
            })
        
        # Event-History
        for event in verlauf.get('events', []):
            events.append({
                'type': 'historie',
                'status': event.get('status', ''),
                'datum': event.get('datum', ''),
                'ruecksendung': event.get('ruecksendung', False)
            })
    
    return events

def find_relevant_status(events: list) -> list:
    """Sucht nach relevanten Status-Schlüsselwörtern"""
    found = []
    
    for event in events:
        status_text = event.get('status', '').lower()
        for keyword in STATUS_KEYWORDS:
            if keyword.lower() in status_text:
                found.append({
                    'keyword': keyword,
                    'status': event.get('status'),
                    'datum': event.get('datum'),
                    'type': event.get('type')
                })
                break
    
    return found

def format_date(date_str: str) -> str:
    """Formatiert ISO-Datum für Anzeige"""
    if not date_str:
        return 'unbekannt'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return date_str

def main():
    parser = argparse.ArgumentParser(description='DHL Sendungsverfolgung via API')
    parser.add_argument('tracking_code', help='DHL Tracking-Nummer (z.B. 00340434886241560288)')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Nur bei Ergebnis ausgeben')
    
    args = parser.parse_args()
    
    # Tracking-Code validieren (DHL: 20 Ziffern)
    if not re.match(r'^\d{20}$', args.tracking_code.strip()):
        print(f"⚠️ Ungültiges Format: {args.tracking_code}")
        print("   DHL Tracking-Nummern sind exakt 20 Ziffern")
        sys.exit(1)
    
    tracking_code = args.tracking_code.strip()
    
    if not args.quiet:
        print(f"📦 DHL Tracker gestartet...")
        print(f"🔍 Tracking-Code: {tracking_code}")
        print(f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
    
    # API abfragen
    data = fetch_tracking_data(tracking_code)
    
    if not data:
        if not args.quiet:
            print("❌ Keine Daten erhalten")
        sys.exit(1)
    
    # Events extrahieren
    events = extract_events(data)
    relevant = find_relevant_status(events)
    
    # Prüfen ob Zustellung erfolgreich
    zugestellt = any('zustellung erfolgreich' in e.get('status', '').lower() or 
                     'zugestellt' in e.get('status', '').lower() for e in events)
    
    # JSON-Output
    if args.json:
        output = {
            'tracking_code': tracking_code,
            'timestamp': datetime.now().isoformat(),
            'zugestellt': zugestellt,
            'events': events,
            'relevant_found': relevant
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return output
    
    # Text-Output
    if relevant or not args.quiet:
        print("=" * 60)
        print(f"🚚 DHL SENDUNGSSTATUS")
        print(f"📦 {tracking_code}")
        print("=" * 60)
        
        if zugestellt:
            print("\n✅ SENDUNG ZUGESTELLT!")
        elif relevant:
            print("\n📍 RELEVANTER STATUS:")
        
        for r in relevant:
            print(f"\n   🚛 {r['status']}")
            print(f"   📅 {format_date(r['datum'])}")
        
        if not zugestellt:
            print("\n📋 Sendungsverlauf:")
            for event in events[-5:]:  # Letzte 5 Events
                icon = "📍" if event['type'] == 'aktuell' else "⏮️"
                status_short = event['status'][:55] + "..." if len(event['status']) > 55 else event['status']
                print(f"   {icon} {format_date(event['datum'])} - {status_short}")
        
        print("=" * 60)
    
    # Rückgabe für weitere Verarbeitung
    return {
        'tracking_code': tracking_code,
        'zugestellt': zugestellt,
        'relevant_found': relevant,
        'events': events
    }

if __name__ == '__main__':
    result = main()
    sys.exit(0 if result else 1)
