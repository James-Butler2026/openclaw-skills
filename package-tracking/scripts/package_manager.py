#!/usr/bin/env python3
"""
Paket-Manager - Zentralisiertes Tracking für Hermes und DHL
Optimiert für Cron-Jobs mit JSON-Output und Telegram-Integration
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from scripts.db_manager import add_package, get_active_packages, update_package_status

def add_new_package(tracking_code: str, carrier: str, description: str = '') -> bool:
    """Fügt neues Paket hinzu und startet automatisches Tracking"""
    carrier = carrier.lower()
    if carrier not in ['dhl', 'hermes']:
        print(f"❌ Ungültiger Carrier: {carrier}")
        return False
    
    if add_package(tracking_code, carrier, description):
        print(f"✅ Paket hinzugefügt: {tracking_code} ({carrier})")
        print(f"   Tracking: 10:00 & 16:00 Uhr")
        return True
    return False

def track_carrier(tracking_code: str, carrier: str, current_status: str) -> Dict[str, Any]:
    """Trackt einzelnes Paket - Generic Funktion für beide Carrier
    
    Args:
        tracking_code: Die Tracking-Nummer
        carrier: 'hermes' oder 'dhl'
        current_status: Aktueller Status aus DB
        
    Returns:
        Update-Dict oder None wenn kein Change
    """
    scripts = {
        'hermes': 'skills/hermes-tracking/scripts/hermes_tracker.py',
        'dhl': 'skills/dhl-tracking/scripts/dhl_tracker.py'
    }
    
    timeouts = {'hermes': 120, 'dhl': 60}
    
    script_path = Path(__file__).parent.parent.parent / scripts[carrier]
    
    try:
        result = subprocess.run(
            ['python3', str(script_path), tracking_code, '--json'],
            capture_output=True,
            text=True,
            timeout=timeouts[carrier]
        )
        
        # stderr für Fehler prüfen
        if result.returncode != 0:
            return None
        
        data = json.loads(result.stdout)
        
        # Bei Fehler im JSON
        if data.get('error'):
            return None
        
        new_status = data.get('status', current_status)
        
        # Status normalisieren
        if carrier == 'dhl':
            new_status = normalize_dhl_status(new_status)
        
        if new_status != current_status:
            # DB aktualisieren
            update_data = {'status': new_status, 'updated_at': datetime.now().isoformat()}
            
            if new_status == 'delivered':
                update_data['delivered'] = 1
                update_data['delivered_at'] = datetime.now().isoformat()
            
            update_package_status(tracking_code, **update_data)
            
            return {
                'code': tracking_code,
                'carrier': carrier.upper(),
                'old_status': current_status,
                'new_status': new_status,
                'status_text': data.get('status_description', new_status),
                'delivered': new_status == 'delivered',
                'timestamp': datetime.now().isoformat()
            }
            
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        return None
    
    return None

def normalize_dhl_status(status: str) -> str:
    """Normalisiert DHL-Status auf gemeinsame Codes"""
    status_lower = status.lower()
    
    if 'zugestellt' in status_lower or 'zustellung erfolgreich' in status_lower:
        return 'delivered'
    elif 'zustellfahrzeug' in status_lower:
        return 'in_delivery'
    elif 'paketzentrum' in status_lower or 'sortiert' in status_lower:
        return 'in_transit'
    return status

def track_all_packages() -> List[Dict[str, Any]]:
    """Trackt alle aktiven Pakete - Hauptfunktion für Cron
    
    Returns:
        Liste von Updates. Bei Zustellung wird Paket automatisch gelöscht.
    """
    packages = get_active_packages()
    updates = []
    
    for pkg in packages:
        tracking_code = pkg['tracking_code']
        carrier = pkg['carrier'].lower()
        current_status = pkg.get('status', '')
        
        update = track_carrier(tracking_code, carrier, current_status)
        if update:
            updates.append(update)
            
            # Bei Zustellung: Cron-Job löschen (Paket bleibt in DB)
            if update.get('delivered'):
                try:
                    import subprocess
                    # Cron-Job für package-tracking löschen
                    result = subprocess.run(
                        ['openclaw', 'cron', 'list'],
                        capture_output=True,
                        text=True
                    )
                    # Hier müsste man den spezifischen Cron-Job finden und löschen
                    print(f"✅ Paket {tracking_code} zugestellt - Cron-Job kann gelöscht werden")
                except Exception as e:
                    print(f"⚠️ Konnte Cron-Job nicht löschen: {e}")
    
    return updates

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Paket-Manager')
    parser.add_argument('action', choices=['add', 'list', 'status', 'track'])
    parser.add_argument('--code', '-c', help='Tracking-Code')
    parser.add_argument('--carrier', '-r', choices=['dhl', 'hermes'])
    parser.add_argument('--desc', '-d', default='')
    parser.add_argument('--json', action='store_true')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        if not args.code or not args.carrier:
            print("❌ Fehlt: --code und --carrier")
            sys.exit(1)
        add_new_package(args.code, args.carrier, args.desc)
    
    elif args.action == 'list':
        packages = get_active_packages()
        if not packages:
            print("📭 Keine aktiven Pakete")
            return
        
        print(f"📦 {len(packages)} aktive Pakete:")
        for pkg in packages:
            print(f"  {pkg['carrier'].upper()}: {pkg['tracking_code']} - {pkg.get('status', 'Unbekannt')}")
    
    elif args.action == 'status':
        packages = get_active_packages()
        print(json.dumps([{
            'code': p['tracking_code'],
            'carrier': p['carrier'],
            'status': p.get('status', 'Unbekannt'),
        } for p in packages], indent=2))
    
    elif args.action == 'track':
        packages = get_active_packages()
        
        if not packages:
            print("📭 Keine aktiven Pakete mehr - Cron-Job wird gelöscht")
            # Cron-Job über Namen löschen
            try:
                import subprocess
                # Zuerst Job-ID finden
                result = subprocess.run(
                    ['openclaw', 'cron', 'list', '--json'],
                    capture_output=True,
                    text=True
                )
                import json
                jobs = json.loads(result.stdout)
                for job in jobs.get('jobs', []):
                    if 'package' in job.get('name', '').lower() or 'paket' in job.get('name', '').lower():
                        job_id = job.get('id')
                        # Job löschen
                        subprocess.run(['openclaw', 'cron', 'remove', job_id], capture_output=True)
                        print(f"🗑️ Cron-Job '{job['name']}' gelöscht")
            except Exception as e:
                print(f"⚠️ Konnte Cron-Job nicht löschen: {e}")
            sys.exit(0)
        
        updates = track_all_packages()
        
        if args.json:
            print(json.dumps(updates, indent=2))
        else:
            for upd in updates:
                icon = '✅' if upd['delivered'] else '🚚'
                print(f"{icon} {upd['carrier']} {upd['code']}: {upd['status_text']}")
        
        # Nach Tracking prüfen ob noch Pakete da sind
        remaining = get_active_packages()
        if not remaining:
            print("📭 Alle Pakete zugestellt - Cron-Job wird gelöscht")
            try:
                import subprocess
                result = subprocess.run(
                    ['openclaw', 'cron', 'list', '--json'],
                    capture_output=True,
                    text=True
                )
                import json
                jobs = json.loads(result.stdout)
                for job in jobs.get('jobs', []):
                    if 'package' in job.get('name', '').lower() or 'paket' in job.get('name', '').lower():
                        job_id = job.get('id')
                        subprocess.run(['openclaw', 'cron', 'remove', job_id], capture_output=True)
                        print(f"🗑️ Cron-Job '{job['name']}' gelöscht")
            except Exception as e:
                print(f"⚠️ Konnte Cron-Job nicht löschen: {e}")

if __name__ == '__main__':
    main()
