#!/usr/bin/env python3
"""
Hermes Sendungsverfolgung - Browser-Automation mit OCR
Extrahiert Status aus Hermes-Tracking-Seite via Playwright + Tesseract

WICHTIG: Dies ist das LOW-LEVEL Tracking-Script für einzelne Pakete.
Für zentrale Verwaltung mehrerer Pakete (Hermes + DHL) siehe:
  -> package_manager.py (im selben Ordner)
  
Verwendung via Manager:
  python3 package_manager.py track --json
"""

import argparse
import sys
import re
import json
import os
from pathlib import Path
from datetime import datetime

# Zentrales Logging importieren
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from logger_config import get_logger

logger = get_logger(__name__)

# Konfiguration
WORKSPACE = Path(os.getenv('OPENCLAW_WORKSPACE', '/home/node/.openclaw/workspace'))
DB_PATH = WORKSPACE / 'data' / 'james.db'

# Status-Muster die wir erkennen
STATUS_PATTERNS = {
    'delivered': [
        r"Die Sendung wurde an der Empfangsadresse zugestellt",
        r"zugestellt",
    ],
    'in_delivery': [
        r"Die Sendung wurde ins Zustellfahrzeug geladen",
        r"zustellfahrzeug",
    ],
    'in_transit': [
        r"Die Sendung ist im Hermes Logistikzentrum",
        r"Zustellbasis",
        r"unterwegs",
    ],
    'picked_up': [
        r"Die Sendung wurde im Paketshop abgeholt",
    ],
    'in_store': [
        r"Die Sendung liegt in der Filiale",
        r"Filial",
    ],
}

def extract_tracking_code(url_or_code: str) -> str:
    """Extrahiert Tracking-Code aus URL oder gibt direkt zurück"""
    if '#' in url_or_code:
        return url_or_code.split('#')[-1].strip()
    if re.match(r'^H\d{16,}$', url_or_code.strip()):
        return url_or_code.strip()
    return url_or_code.strip()

def detect_status(ocr_text: str) -> tuple:
    """Erkennt Paket-Status aus OCR-Text
    
    Returns:
        tuple: (status_code, status_description)
    """
    text_lower = ocr_text.lower()
    
    # Priorisierte Reihenfolge: delivered > in_delivery > in_transit
    for status_code, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return status_code, pattern
    
    return 'unknown', 'Status unbekannt'

def track_hermes(tracking_code: str, headless: bool = True) -> dict:
    """Trackt Hermes-Paket und gibt strukturierte Daten zurück
    
    Args:
        tracking_code: Hermes Tracking-Nummer (H...)
        headless: Browser im Hintergrund laufen lassen
        
    Returns:
        dict mit tracking_code, status, timestamp, screenshot
    """
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import pytesseract
    
    tracking_url = f"https://www.myhermes.de/empfangen/sendungsverfolgung/sendungsinformation#{tracking_code}"
    
    # Screenshot-Pfad
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = Path(f"/tmp/hermes_{tracking_code}_{timestamp}.png")
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starte Tracking für {tracking_code}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        try:
            # Seite laden
            page.goto(tracking_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)  # JS laden
            
            # Cookie-Banner
            try:
                cookie_btn = page.locator('button:has-text("Akzeptieren"), button:has-text("Alle akzeptieren")').first
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
            except:
                pass
            
            # Screenshot
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Screenshot gespeichert: {screenshot_path}")
            
        except Exception as e:
            logger.error(f"Browser-Fehler: {e}")
            browser.close()
            raise
        
        browser.close()
    
    # OCR
    try:
        img = Image.open(screenshot_path)
        ocr_text = pytesseract.image_to_string(img, lang='deu')
        logger.debug(f"OCR erkannt: {ocr_text[:200]}...")
    except Exception as e:
        logger.error(f"OCR fehlgeschlagen: {e}")
        ocr_text = ""
    
    # Status erkennen
    status_code, status_desc = detect_status(ocr_text)
    
    # Datum extrahieren
    date_pattern = r'\d{2}\.\d{2}\.\d{4}'
    dates_found = list(set(re.findall(date_pattern, ocr_text)))[:3]
    
    result = {
        'tracking_code': tracking_code,
        'carrier': 'hermes',
        'status': status_code,
        'status_description': status_desc,
        'timestamp': datetime.now().isoformat(),
        'screenshot': str(screenshot_path),
        'dates_found': dates_found,
        'ocr_text_preview': ocr_text[:500],
    }
    
    logger.info(f"Tracking Ergebnis: {status_code}")
    return result

def main():
    parser = argparse.ArgumentParser(description='Hermes Sendungsverfolgung mit OCR')
    parser.add_argument('tracking_code', help='Hermes Tracking-Nummer')
    parser.add_argument('--headless', action='store_true', default=True, help='Headless-Modus')
    parser.add_argument('--show-browser', action='store_true', help='Browser sichtbar')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')
    
    args = parser.parse_args()
    
    # Validierung
    tracking_code = extract_tracking_code(args.tracking_code)
    if not re.match(r'^H\d{16,}$', tracking_code):
        error_msg = f"Ungültige Tracking-Nummer: {tracking_code}. Format: H + 16+ Ziffern"
        if args.json:
            print(json.dumps({'error': True, 'message': error_msg}))
        else:
            print(f"❌ {error_msg}")
        sys.exit(1)
    
    try:
        result = track_hermes(tracking_code, headless=(args.headless and not args.show_browser))
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("=" * 60)
            print(f"🚚 HERMES SENDUNGSSTATUS")
            print(f"📦 {tracking_code}")
            print(f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            print("=" * 60)
            print(f"\n✅ Status: {result['status']}")
            print(f"   {result['status_description']}")
            if result['dates_found']:
                print(f"\n📅 Daten: {', '.join(result['dates_found'])}")
            print(f"\n📁 Screenshot: {result['screenshot']}")
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
    sys.exit(0)
