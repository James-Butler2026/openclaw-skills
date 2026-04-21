#!/usr/bin/env python3
"""
Hermes Sendungsverfolgung - Browser-Automation mit OCR
Extrahiert Status aus Hermes-Tracking-Seite via Playwright + Tesseract
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime


# Zentrales Logging importieren
sys.path.insert(0, '/home/node/.openclaw/workspace/scripts')
from logger_config import get_logger

logger = get_logger(__name__)


def extract_tracking_code(url_or_code: str) -> str:
    """Extrahiert Tracking-Code aus URL oder gibt direkt zurück"""
    # Wenn es eine URL ist, versuche den Code zu extrahieren
    if '#' in url_or_code:
        return url_or_code.split('#')[-1].strip()
    # Direkter Code (H + 18+ Ziffern)
    if re.match(r'^H\d{16,}$', url_or_code.strip()):
        return url_or_code.strip()
    return url_or_code.strip()

def main():
    parser = argparse.ArgumentParser(description='Hermes Sendungsverfolgung mit OCR')
    parser.add_argument('tracking_code', help='Hermes Tracking-Nummer oder vollständige URL')
    parser.add_argument('--headless', action='store_true', default=True, help='Headless-Modus (default: True)')
    parser.add_argument('--show-browser', action='store_true', help='Browser-Fenster anzeigen')
    parser.add_argument('--output', '-o', help='Screenshot-Pfad (optional)')
    
    args = parser.parse_args()
    
    # Tracking-Code extrahieren
    tracking_code = extract_tracking_code(args.tracking_code)
    
    if not re.match(r'^H\d{16,}$', tracking_code):
        print(f"❌ Ungültige Tracking-Nummer: {tracking_code}")
        print("   Format: H gefolgt von 16+ Ziffern (z.B. [DEINE_TRACKING_NUMMER])")
        sys.exit(1)
    
    # URL aufbauen
    tracking_url = f"https://www.myhermes.de/empfangen/sendungsverfolgung/sendungsinformation#{tracking_code}"
    
    print(f"🚚 Hermes Tracker gestartet...")
    print(f"📦 Tracking-Code: {tracking_code}")
    print(f"🌐 URL: {tracking_url}")
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright nicht installiert. Installiere mit:")
        print("   pip install playwright")
        print("   playwright install chromium")
        sys.exit(1)
    
    # Screenshot-Pfad
    if args.output:
        screenshot_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = Path(f"/tmp/hermes_{tracking_code}_{timestamp}.png")
    
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Browser-Automation
    print("🎭 Starte Browser...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless and not args.show_browser)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            # Seite laden
            print(f"⏳ Lade Hermes-Seite...")
            page.goto(tracking_url, wait_until='networkidle', timeout=30000)
            
            # Warten bis Tracking-Informationen geladen sind
            print(f"⏳ Warte auf Sendungsdaten...")
            page.wait_for_timeout(3000)  # 3 Sekunden für JavaScript
            
            # Cookie-Banner akzeptieren (falls vorhanden)
            try:
                cookie_btn = page.locator('button:has-text("Akzeptieren"), button:has-text("Alle akzeptieren"), button:has-text("Verstanden")').first
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
                    print("🍪 Cookie-Banner akzeptiert")
            except:
                pass
            
            # Screenshot der Seite
            print(f"📸 Erstelle Screenshot...")
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"💾 Screenshot gespeichert: {screenshot_path}")
            
            # Seitentitel extrahieren
            title = page.title()
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Seite: {e}")
            browser.close()
            sys.exit(1)
        
        browser.close()
    
    # OCR durchführen
    print(f"🔍 Führe OCR durch...")
    
    try:
        import pytesseract
        from PIL import Image
        
        img = Image.open(screenshot_path)
        ocr_text = pytesseract.image_to_string(img, lang='deu')
        
    except Exception as e:
        print(f"⚠️ OCR fehlgeschlagen: {e}")
        print(f"   Screenshot wurde gespeichert unter: {screenshot_path}")
        ocr_text = ""
    
    # Status-Sätze suchen
    print(f"📋 Analysiere Status...\n")
    
    status_patterns = [
        r"Die Sendung wurde an der Empfangsadresse zugestellt",
        r"Die Sendung wurde ins Zustellfahrzeug geladen und wird voraussichtlich heute zugestellt",
        r"Die Sendung wurde im Paketshop abgeholt",
        r"Die Sendung liegt in der Filiale bereit zur Abholung",
        r"Die Sendung wurde vom Absender an Hermes übergeben",
        r"Die Sendung ist im Hermes Logistikzentrum eingegangen",
        r"Die Sendung ist in der Zustellbasis angekommen",
    ]
    
    found_status = []
    
    for pattern in status_patterns:
        if re.search(pattern, ocr_text, re.IGNORECASE):
            found_status.append(pattern)
    
    # Ergebnis ausgeben
    print("=" * 60)
    print(f"🚚 HERMES SENDUNGSSTATUS")
    print(f"📦 Tracking: {tracking_code}")
    print(f"🕐 Zeit: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 60)
    
    if found_status:
        print("\n✅ STATUS ERKANNT:")
        for status in found_status:
            print(f"   • {status}")
    else:
        print("\n⚠️ Kein bekannter Status-Text gefunden")
        print("   Screenshot wurde zur manuellen Prüfung gespeichert.")
    
    # Zusätzliche Info aus dem OCR-Text
    date_pattern = r'\d{2}\.\d{2}\.\d{4}'
    dates_found = re.findall(date_pattern, ocr_text)
    
    if dates_found:
        unique_dates = list(set(dates_found))[:3]
        print(f"\n📅 Gefundene Daten: {', '.join(unique_dates)}")
    
    print(f"\n📁 Screenshot: {screenshot_path}")
    print("=" * 60)
    
    # Rückgabe für weitere Verarbeitung
    return {
        'tracking_code': tracking_code,
        'status': found_status,
        'screenshot': str(screenshot_path),
        'ocr_text': ocr_text[:2000]  # Erste 2000 Zeichen
    }

if __name__ == '__main__':
    result = main()
    sys.exit(0 if result and result['status'] else 1)
