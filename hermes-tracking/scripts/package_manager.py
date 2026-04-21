#!/usr/bin/env python3
"""
Paket-Manager
Verwaltet Pakete und dynamische Cron-Jobs für Tracking
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/node/.openclaw/workspace')
from scripts.db_manager import add_package, get_active_packages, update_package_status

def add_new_package(tracking_code, carrier, description=''):
    """Fügt neues Paket hinzu und startet Tracking"""
    
    # Validierung
    carrier = carrier.lower()
    if carrier not in ['dhl', 'hermes']:
        print(f"❌ Ungültiger Carrier: {carrier}")
        print("   Erlaubt: dhl, hermes")
        return False
    
    # In DB speichern
    success = add_package(tracking_code, carrier, description)
    
    if success:
        print(f"✅ Paket hinzugefügt: {tracking_code} ({carrier})")
        print(f"   Beschreibung: {description or 'Keine'}")
        print(f"   Tracking läuft automatisch um 10:00 und 16:00")
        print(f"   ✨ Sie werden benachrichtigt bei Status-Änderungen")
        return True
    else:
        print(f"ℹ️  Paket bereits vorhanden oder Fehler")
        return False

def list_packages():
    """Zeigt alle aktiven Pakete"""
    packages = get_active_packages()
    
    if not packages:
        print("📭 Keine aktiven Pakete")
        return
    
    print(f"📦 Aktive Pakete: {len(packages)}")
    print("=" * 60)
    
    for i, pkg in enumerate(packages, 1):
        status = pkg.get('status', 'Unbekannt')
        desc = pkg.get('description', '')
        carrier = pkg.get('carrier', '').upper()
        updated = pkg.get('updated_at', 'Nie')
        
        print(f"{i}. {carrier}: {pkg['tracking_code']}")
        print(f"   Status: {status}")
        if desc:
            print(f"   Beschreibung: {desc}")
        print(f"   Letztes Update: {updated}")
        print()

def track_all_packages():
    """Trackt alle aktiven Pakete - für Cron-Job (Hermes + DHL)"""
    import subprocess
    
    packages = get_active_packages()
    updates = []
    
    for pkg in packages:
        tracking_code = pkg['tracking_code']
        carrier = pkg['carrier'].lower()
        current_status = pkg.get('status', '')
        
        if carrier == 'hermes':
            # Hermes tracken mit JSON Output
            result = subprocess.run(
                ['python3', '/home/node/.openclaw/workspace/scripts/hermes_tracker.py', tracking_code, '--json'],
                capture_output=True, text=True, timeout=120
            )
            
            try:
                data = json.loads(result.stdout)
                new_status = data.get('status', current_status)
                
                if new_status != current_status:
                    update_package_status(tracking_code, new_status)
                    updates.append({
                        'code': tracking_code,
                        'carrier': 'HERMES',
                        'old_status': current_status,
                        'new_status': new_status,
                        'status_text': new_status,
                        'delivered': 'zugestellt' in new_status.lower() or 'delivered' in new_status.lower()
                    })
            except json.JSONDecodeError:
                pass
        
        elif carrier == 'dhl':
            # DHL tracken (falls DHL Script existiert)
            try:
                result = subprocess.run(
                    ['python3', '/home/node/.openclaw/workspace/scripts/dhl_tracker.py', tracking_code, '--json'],
                    capture_output=True, text=True, timeout=60
                )
                
                try:
                    data = json.loads(result.stdout)
                    new_status = data.get('status', current_status)
                    
                    if new_status != current_status:
                        update_package_status(tracking_code, new_status)
                        updates.append({
                            'code': tracking_code,
                            'carrier': 'DHL',
                            'old_status': current_status,
                            'new_status': new_status,
                            'status_text': new_status,
                            'delivered': 'zugestellt' in new_status.lower() or 'delivered' in new_status.lower()
                        })
                except json.JSONDecodeError:
                    pass
            except FileNotFoundError:
                # DHL Tracker existiert noch nicht - überspringen
                pass
    
    return updates

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Paket-Manager')
    parser.add_argument('action', choices=['add', 'list', 'status', 'track'], 
                       help='Aktion: add, list, status, track')
    parser.add_argument('--code', '-c', help='Tracking-Code')
    parser.add_argument('--carrier', '-r', choices=['dhl', 'hermes'],
                       help='Carrier: dhl oder hermes')
    parser.add_argument('--desc', '-d', default='', help='Beschreibung')
    parser.add_argument('--json', action='store_true', help='JSON Output für track')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        if not args.code or not args.carrier:
            print("❌ Fehlt: --code und --carrier")
            print("   Beispiel: python3 package_manager.py add -c [DEINE_TRACKING_NUMMER] -r dhl -d 'Amazon'")
            sys.exit(1)
        
        add_new_package(args.code, args.carrier, args.desc)
    
    elif args.action == 'list':
        list_packages()
    
    elif args.action == 'status':
        # Zeigt Status aus DB
        packages = get_active_packages()
        print(json.dumps([{
            'code': p['tracking_code'],
            'carrier': p['carrier'],
            'status': p.get('status', 'Unbekannt'),
            'description': p.get('description', ''),
            'last_update': p.get('updated_at', '')
        } for p in packages], indent=2, ensure_ascii=False))
    
    elif args.action == 'track':
        # Cron-Modus: Trackt alle aktiven Pakete
        updates = track_all_packages()
        
        if args.json:
            print(json.dumps(updates, indent=2, ensure_ascii=False))
        else:
            for upd in updates:
                print(f"UPDATE: {upd['carrier']} {upd['code']} - {upd['status_text']}")

if __name__ == '__main__':
    main()
