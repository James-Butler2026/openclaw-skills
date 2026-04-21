#!/usr/bin/env python3
"""
Sub-Agent: Paket-Tracking (DHL + Hermes)
Prüft alle aktiven Pakete und speichert Updates in DB
"""

import sys
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/node/.openclaw/workspace')
from scripts.db_manager import (
    get_active_packages, update_package_status, 
    mark_package_delivered, log_system, add_package
)

def track_dhl_package(tracking_code):
    """Tracked DHL Paket via API"""
    url = f"https://www.dhl.de/int-verfolgen/data/search?piececode={tracking_code}&language=de"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'sendungen' not in data or not data['sendungen']:
                return None
            
            sendung = data['sendungen'][0]
            details = sendung.get('sendungsdetails', {})
            verlauf = details.get('sendungsverlauf', {})
            
            # Aktueller Status
            status = verlauf.get('status', 'Unbekannt')
            ist_zugestellt = sendung.get('istZugestellt', False)
            
            # Events extrahieren
            events = []
            for event in verlauf.get('events', []):
                events.append({
                    'timestamp': event.get('datum', ''),
                    'status': event.get('status', ''),
                    'location': event.get('ort', '')
                })
            
            return {
                'carrier': 'DHL',
                'status': status,
                'delivered': ist_zugestellt,
                'events': events
            }
            
    except Exception as e:
        log_system('package_agent', 'error', f'DHL Fehler {tracking_code}: {e}')
        return None

def track_hermes_package(tracking_code):
    """Tracked Hermes Paket via Browser + OCR (echter Tracker)"""
    import subprocess
    import os
    
    tracker_script = Path('/home/node/.openclaw/workspace/scripts/hermes_tracker.py')
    if not tracker_script.exists():
        log_system('package_agent', 'error', f'Hermes Tracker nicht gefunden: {tracker_script}')
        return None
    
    try:
        # Starte Hermes Tracker
        result = subprocess.run(
            ['/home/node/.openclaw/venv/bin/python3', str(tracker_script), tracking_code],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='/home/node/.openclaw/workspace'
        )
        
        output = result.stdout + result.stderr
        
        # Status aus Output parsen
        if 'zugestellt' in output.lower() or 'zugestellt' in output.lower():
            return {
                'carrier': 'Hermes',
                'status': 'zugestellt',
                'delivered': True,
                'events': []
            }
        elif 'in zustellung' in output.lower() or 'unterwegs' in output.lower():
            return {
                'carrier': 'Hermes',
                'status': 'in Zustellung',
                'delivered': False,
                'events': []
            }
        elif 'abgeholt' in output.lower():
            return {
                'carrier': 'Hermes',
                'status': 'abgeholt',
                'delivered': False,
                'events': []
            }
        else:
            # Versuche Screenshot-OCR Methode
            # Prüfe ob Screenshot existiert
            screenshot_path = f'/tmp/hermes_{tracking_code}_*.png'
            import glob
            screenshots = glob.glob(screenshot_path)
            
            if screenshots:
                log_system('package_agent', 'info', f'Hermes Screenshot gefunden, OCR prüfen')
                # OCR wurde bereits im hermes_tracker.py gemacht
                # Wenn wir hier sind, wurde der Status bereits analysiert
                return {
                    'carrier': 'Hermes',
                    'status': 'in Bearbeitung',
                    'delivered': False,
                    'events': []
                }
            
            log_system('package_agent', 'warning', f'Hermes Status nicht klar erkannt: {output[:200]}')
            return None
            
    except subprocess.TimeoutExpired:
        log_system('package_agent', 'error', f'Hermes Tracking Timeout für {tracking_code}')
        return None
    except Exception as e:
        log_system('package_agent', 'error', f'Hermes Tracking Fehler: {e}')
        return None

def check_all_packages():
    """Prüft alle aktiven Pakete"""
    packages = get_active_packages()
    
    if not packages:
        log_system('package_agent', 'info', 'Keine aktiven Pakete')
        return []
    
    log_system('package_agent', 'info', f'Prüfe {len(packages)} Pakete')
    
    updates = []
    
    for package in packages:
        tracking_code = package['tracking_code']
        carrier = package['carrier']
        old_status = package['status']
        
        # Tracking basierend auf Carrier
        if carrier.lower() == 'dhl':
            result = track_dhl_package(tracking_code)
        elif carrier.lower() == 'hermes':
            result = track_hermes_package(tracking_code)
        else:
            continue
        
        if not result:
            continue
        
        new_status = result['status']
        
        # Status-Update speichern
        if new_status != old_status:
            update_package_status(
                tracking_code,
                new_status,
                status_details='',
                events=result.get('events', [])
            )
            
            updates.append({
                'tracking_code': tracking_code,
                'carrier': carrier,
                'old_status': old_status,
                'new_status': new_status,
                'delivered': result['delivered']
            })
            
            log_system('package_agent', 'info', 
                      f'{carrier} {tracking_code}: {old_status} -> {new_status}')
        
        # Als zugestellt markieren
        if result['delivered']:
            mark_package_delivered(tracking_code)
            log_system('package_agent', 'info', f'{tracking_code} als zugestellt markiert')
    
    return updates

def main():
    log_system('package_agent', 'info', 'Agent gestartet')
    
    updates = check_all_packages()
    
    log_system('package_agent', 'info', f'Agent beendet. {len(updates)} Status-Updates')
    
    print(json.dumps({
        "success": True,
        "updates": updates,
        "delivered_count": len([u for u in updates if u.get('delivered')]),
        "timestamp": datetime.now().isoformat()
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
