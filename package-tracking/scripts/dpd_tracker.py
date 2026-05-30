#!/usr/bin/env python3
"""
DPD Sendungsverfolgung - Browser-Automation
Extrahiert Status aus DPD-Tracking-Seite via Playwright
Kein API-Key nötig - nutzt öffentliche DPD Tracking-Seite

Optional: PLZ für erweiterte Status-Informationen (93173 = Wenzenbach)

Verwendung:
  python3 dpd_tracker.py 09450012345678
  python3 dpd_tracker.py 09450012345678 --json
  python3 dpd_tracker.py 09450012345678 --plz 93173 --json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Status-Muster für DPD
STATUS_PATTERNS = {
    'delivered': [
        r"zugestellt",
        r"geliefert",
        r"wurde zugestellt",
        r"Die Sendung wurde zugestellt",
        r"Zustellung erfolgreich",
    ],
    'in_delivery': [
        r"im Zustellfahrzeug",
        r"wird zugestellt",
        r"im Fahrzeug",
        r"letzte Meile",
    ],
    'in_transit': [
        r"im Sortierzentrum",
        r"in der Niederlassung",
        r"auf dem Weg",
        r"Transport",
        r"Sortier",
        r"unterwegs",
        r"bearbeitet",
        r"angekündigt",
        r"elektronisch angekündigt",
        r"Auftragsdaten",
    ],
    'out_for_delivery': [
        r"ausgeliefert",
        r"Delivery",
        r"Zustellbasis",
    ],
    'in_store': [
        r"Paketshop",
        r"Abholstation",
        r"Filiale",
        r"liegt bereit",
        r"zur Abholung",
    ],
    'problem': [
        r"Problem",
        r"Fehler",
        r"nicht zugestellt",
        r"Adressproblem",
        r"Verzögerung",
    ],
}

TRACKING_URL = "https://www.dpd.com/de/de/empfangen/sendungsverfolgung-und-live-tracking/"
DEFAULT_PLZ = "93173"  # Wenzenbach / Regenstauf


def extract_tracking_code(code: str) -> str:
    """Extrahiert Tracking-Code aus Eingabe"""
    code = code.strip()
    # Wenn URL, Paketnummer parsen
    if 'dpd.de' in code or 'dpd.com' in code:
        # Letzer Pfad-Teil als Nummer
        match = re.search(r'/parcel/(\d{14,})', code)
        if match:
            return match.group(1)
    return code


def detect_status(text: str) -> tuple:
    """Erkennt Paket-Status aus Text
    
    Returns:
        tuple: (status_code, status_description)
    """
    text_lower = text.lower()
    
    for status_code, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return status_code, pattern
    
    return 'unknown', 'Status unbekannt'


def track_dpd(tracking_code: str, plz: str = None) -> dict:
    """Trackt DPD-Paket und gibt strukturierte Daten zurück
    
    Args:
        tracking_code: DPD Tracking-Nummer (14-stellig)
        plz: Optional PLZ der Empfangsadresse für genauere Daten
        
    Returns:
        dict mit tracking_code, status, timestamp
    """
    from playwright.sync_api import sync_playwright
    
    result = {
        'tracking_code': tracking_code,
        'carrier': 'dpd',
        'status': 'unknown',
        'status_description': '',
        'status_text': '',
        'timestamp': datetime.now().isoformat(),
        'events': [],
        'error': False,
        'error_message': '',
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # Schritt 1: Startseite öffnen
            page.goto(TRACKING_URL, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            
            # Consent-Manager Overlay entfernen
            try:
                page.evaluate("""
                    var w = document.getElementById('cmpwrapper');
                    if (w) w.remove();
                    var q = document.querySelector('.cmpwrapper');
                    if (q) q.remove();
                """)
                page.wait_for_timeout(500)
            except:
                pass
            
            # Schritt 2: Trackingnummer eingeben
            search_input = page.locator('input[placeholder*="Paketnummer"]').first
            search_input.fill(tracking_code)
            page.wait_for_timeout(200)
            search_input.press("Enter")
            page.wait_for_timeout(3000)
            
            # Schritt 3: PLZ eingeben (wenn angegeben) oder "Weiter ohne PLZ"
            plz_field = page.locator('#ContentPlaceHolder1_txtDataprotectionZipCode')
            
            if plz_field.is_visible(timeout=5000):
                if plz:
                    # PLZ eingeben
                    plz_field.fill(plz)
                    page.wait_for_timeout(300)
                    
                    # Formular per JS submiten (__doPostBack)
                    page.evaluate("""
                        (function() {
                            var form = document.getElementById('form1');
                            var target = document.createElement('input');
                            target.type = 'hidden';
                            target.name = '__EVENTTARGET';
                            target.value = 'ctl00$ContentPlaceHolder1$btnCheckZipCode';
                            form.appendChild(target);
                            var arg = document.createElement('input');
                            arg.type = 'hidden';
                            arg.name = '__EVENTARGUMENT';
                            arg.value = '';
                            form.appendChild(arg);
                            form.submit();
                        })();
                    """)
                else:
                    # "Weiter ohne PLZ"
                    page.evaluate("""
                        document.getElementById('ContentPlaceHolder1_btnWithOutZipCode')?.click();
                    """)
                
                page.wait_for_timeout(8000)
            
            # Schritt 4: Ergebnis auslesen
            body_text = page.inner_text('body')
            current_url = page.url
            
            result['status_text'] = body_text[:3000]
            
            # Status erkennen
            status_code, status_desc = detect_status(body_text)
            result['status'] = status_code
            result['status_description'] = status_desc
            
            # Nach Fehlermeldungen suchen
            if "keine Daten" in body_text.lower() or "nicht finden" in body_text.lower():
                result['error'] = False  # Kein echter Fehler - Paket einfach nicht in DB
                if result['status'] == 'unknown':
                    result['status'] = 'not_found'
                    result['status_description'] = 'Keine Daten zu dieser Sendungsnummer'
            
            # Datum extrahieren
            date_patterns = [
                r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
                r'\d{4}-\d{2}-\d{2}',     # YYYY-MM-DD
            ]
            dates_found = []
            for dp in date_patterns:
                dates_found.extend(re.findall(dp, body_text))
            result['dates_found'] = list(set(dates_found))[:5]
            
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        browser.close()
    
    return result


def main():
    parser = argparse.ArgumentParser(description='DPD Sendungsverfolgung')
    parser.add_argument('tracking_code', help='DPD Tracking-Nummer')
    parser.add_argument('--plz', '-p', default=None, 
                       help=f'PLZ der Empfangsadresse (Default: keine)')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Nur Status ausgeben')
    
    args = parser.parse_args()
    
    tracking_code = extract_tracking_code(args.tracking_code)
    
    try:
        result = track_dpd(tracking_code, plz=args.plz)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.quiet:
            print(result['status'])
        else:
            print("=" * 60)
            print(f"🚚 DPD SENDUNGSSTATUS")
            print(f"📦 {tracking_code}")
            print(f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            print("=" * 60)
            
            icon = {
                'delivered': '✅',
                'in_delivery': '🚚',
                'out_for_delivery': '📬',
                'in_transit': '📦',
                'in_store': '🏪',
                'problem': '⚠️',
                'not_found': '🔍',
                'unknown': '❓',
            }.get(result['status'], '❓')
            
            print(f"\n{icon} Status: {result['status']}")
            print(f"   {result['status_description']}")
            
            if result['dates_found']:
                print(f"\n📅 Daten: {', '.join(result['dates_found'])}")
            
            if result['error']:
                print(f"\n❌ Fehler: {result['error_message']}")
                
    except Exception as e:
        error_result = {
            'error': True,
            'message': str(e),
            'tracking_code': tracking_code,
            'carrier': 'dpd',
        }
        if args.json:
            print(json.dumps(error_result, ensure_ascii=False))
        else:
            print(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
