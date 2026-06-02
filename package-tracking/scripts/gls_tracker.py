#!/usr/bin/env python3
"""
GLS Sendungsverfolgung via Browser-Automation + OCR
Extrahiert Status aus GLS-Tracking-Seite via Playwright + Tesseract
Fallback für die kaputte GLS REST API
"""

import argparse
import sys
import re
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime

from logger_config import get_logger

logger = get_logger(__name__)

WORKSPACE = Path(__file__).parent.parent.parent.parent
DB_PATH = WORKSPACE / 'data' / 'packages.db'

STATUS_PATTERNS = {
    'delivered': [
        r"zugestellt",
        r"Die Sendung wurde.*zugestellt",
    ],
    'in_delivery': [
        r"ins Zustellfahrzeug geladen",
        r"Zustellfahrzeug",
    ],
    'in_transit': [
        r"Paketzentrum",
        r"im Paketzentrum eingetroffen",
        r"manuell sortiert",
        r"Sortier",
        r"verteilt",
    ],
    'picked_up': [
        r"abgeholt",
        r"durch GLS übernommen",
    ],
    'announced': [
        r"Paketdaten.*erfasst",
        r"elektronisch angekündigt",
        r"zur Abholung.*bereitgestellt",
    ],
}


def update_db_delivered(tracking_code: str):
    """Markiert Paket als delivered direkt in der DB"""
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
    if '#' in raw:
        return raw.split('#')[-1].strip()
    m = re.search(r'(\d{8,20})', raw)
    if m:
        return m.group(1)
    return raw


def extract_postcode(raw: str) -> str:
    """Extrahiert PLZ aus URL oder Input"""
    m = re.search(r'postCode=(\d{5})', raw)
    if m:
        return m.group(1)
    parts = re.split(r'[/#?&=]', raw)
    for i, part in enumerate(parts):
        if part.lower() in ('postcode', 'postalcode', 'plz', 'post_code'):
            if i + 1 < len(parts):
                return parts[i + 1]
    return ''


def detect_status(ocr_text: str) -> tuple:
    """Erkennt Paket-Status aus OCR-Text"""
    text_lower = ocr_text.lower()
    for status_code, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return status_code, pattern
    return 'unknown', 'Status unbekannt'


def track_gls(tracking_code: str, post_code: str = '', headless: bool = True) -> dict:
    """Trackt GLS-Paket via Browser + Screenshot + OCR"""
    code = extract_tracking_code(tracking_code)
    plz = post_code or extract_postcode(tracking_code)

    if not plz:
        return {'error': True, 'message': 'Postleitzahl erforderlich für GLS-Tracking'}

    url = f"https://www.gls-pakete.de/reach-sendungsverfolgung?trackingNumber={code}&postCode={plz}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = Path(f"/tmp/gls_{code}_{timestamp}.png")
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"GLS Tracking: {code} mit PLZ {plz}")

    from playwright.sync_api import sync_playwright
    from PIL import Image
    import pytesseract

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 1200},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(4000)

            # Cookie-Banner
            try:
                cookie_btn = page.locator('button:has-text("Akzeptieren"), button:has-text("Alle akzeptieren"), button:has-text("Accept")').first
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
                    page.wait_for_timeout(1000)
            except:
                pass

            # Warten auf Tracking-Ergebnisse
            try:
                page.wait_for_selector('table, .progress, .tracking-step, .status, .event, [class*="tracking"]', timeout=10000)
                page.wait_for_timeout(2000)
            except:
                logger.info("Tracking-Selector nicht gefunden, Screenshot trotzdem")

            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Screenshot: {screenshot_path}")

        except Exception as e:
            logger.error(f"Browser-Fehler: {e}")
            browser.close()
            return {'error': True, 'message': f'Browser-Fehler: {e}'}

        browser.close()

    # OCR
    try:
        img = Image.open(screenshot_path)
        ocr_text = pytesseract.image_to_string(img, lang='deu')
        logger.debug(f"OCR ({len(ocr_text)} chars): {ocr_text[:300]}...")
    except Exception as e:
        logger.error(f"OCR-Fehler: {e}")
        ocr_text = ''

    status_code, status_desc = detect_status(ocr_text)

    # Events aus OCR parsen
    events = []
    event_pattern = r'(.+?)\n(.+?)\n(\d{1,2}\.\d{1,2}\.\d{4}).*?(\d{1,2}:\d{2})'
    for m in re.finditer(event_pattern, ocr_text, re.MULTILINE):
        events.append({
            'status': m.group(1).strip()[:80],
            'location': m.group(2).strip()[:40] if m.group(2) else '',
            'date': f"{m.group(3)} {m.group(4)}",
        })

    # Fallback: Einfache Zeilen parsen
    if not events:
        lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]
        for line in lines:
            if re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', line):
                events.append({
                    'status': re.sub(r'\d{1,2}\.\d{1,2}\.\d{4}.*', '', line).strip()[:80],
                    'location': '',
                    'date': re.search(r'(\d{1,2}\.\d{1,2}\.\d{4}.*?\d{1,2}:\d{2})', line).group(1) if re.search(r'(\d{1,2}\.\d{1,2}\.\d{4}.*?\d{1,2}:\d{2})', line) else '',
                })

    # Datum extrahieren
    dates_found = list(set(re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', ocr_text)))[:5]

    # DB-Update bei Zustellung
    if status_code == 'delivered':
        update_db_delivered(code)

    result = {
        'tracking_code': code,
        'carrier': 'gls',
        'status': status_code,
        'status_description': status_desc,
        'timestamp': datetime.now().isoformat(),
        'screenshot': str(screenshot_path),
        'dates_found': dates_found,
        'events': events,
        'ocr_text_preview': ocr_text[:1000],
    }

    logger.info(f"GLS Ergebnis: {status_code} ({len(events)} Events)")
    return result


def main():
    parser = argparse.ArgumentParser(description='GLS Sendungsverfolgung mit Browser + OCR')
    parser.add_argument('tracking_code', help='GLS Tracking-Nummer oder URL')
    parser.add_argument('--postal', '-p', default='', help='Postleitzahl')
    parser.add_argument('--headless', action='store_true', default=True, help='Headless-Modus')
    parser.add_argument('--show-browser', action='store_true', help='Browser sichtbar')
    parser.add_argument('--json', '-j', action='store_true', help='JSON-Output')

    args = parser.parse_args()
    result = track_gls(args.tracking_code, args.postal, headless=(args.headless and not args.show_browser))

    if result.get('error'):
        if args.json:
            print(json.dumps(result))
        else:
            print(f"❌ {result['message']}")
        sys.exit(1)

    if args.json:
        clean = {k: v for k, v in result.items() if k != 'ocr_text_preview'}
        print(json.dumps(clean, indent=2, ensure_ascii=False))
    else:
        icon = {
            'delivered': '✅', 'in_delivery': '🚚', 'in_transit': '📦',
            'picked_up': '📤', 'in_store': '🏪', 'announced': '📋',
            'exception': '⚠️',
        }.get(result['status'], '📦')

        print("=" * 60)
        print(f"{icon} GLS SENDUNGSSTATUS (Browser + OCR)")
        print(f"📦 {result['tracking_code']}")
        print("=" * 60)
        print(f"\n✅ Status: {result['status_description']}")
        print(f"   Code: {result['status']}")
        if result.get('events'):
            print(f"\n📋 Letzte Updates:")
            for evt in result['events'][:5]:
                d = evt['date'] if evt['date'] else ''
                s = evt['status'][:60] if evt['status'] else ''
                l = f" ({evt['location']})" if evt.get('location') else ''
                print(f"   • {d}{l}: {s}")
        if result.get('dates_found'):
            print(f"\n📅 Daten: {', '.join(result['dates_found'])}")
        print(f"\n📸 Screenshot: {result['screenshot']}")
        print("=" * 60)

    return result


if __name__ == '__main__':
    result = main()
    sys.exit(0 if not result.get('error') else 1)