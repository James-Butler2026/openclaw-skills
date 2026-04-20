#!/usr/bin/env python3
"""
Importiert bestehende Termine aus Cron-Jobs in den OpenClaw Calendar.
"""

import sys
import os
import re
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_calendar import Calendar

def parse_cron_jobs():
    """Parst Cron-Jobs und extrahiert Termine."""
    
    cron_file = os.path.expanduser("~/.openclaw/workspace/cron/jobs.json")
    
    try:
        with open(cron_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Konnte Cron-Jobs nicht laden: {e}")
        return []
    
    events = []
    
    for job in data.get('jobs', []):
        name = job.get('name', '')
        payload = job.get('payload', {})
        text = payload.get('text', '')
        
        # Überspringe nicht-Kalender Jobs
        if not any(keyword in text.lower() for keyword in ['termin', 'geburtstag', 'erinnerung', 'dr. kaufmann']):
            continue
        
        # Extrahiere Event Details
        event = parse_event_from_job(job)
        if event:
            events.append(event)
    
    return events

def parse_event_from_job(job):
    """Extrahiert Event-Daten aus einem Cron-Job."""
    
    name = job.get('name', '')
    payload = job.get('payload', {})
    text = payload.get('text', '')
    schedule = job.get('schedule', {})
    
    event = {
        'title': '',
        'date': None,
        'time': None,
        'category': 'Termin',
        'recurrence': 'none',
        'reminder_minutes': None,
        'cron_job_id': job.get('id')
    }
    
    # Dr. Kaufmann Termin
    if 'dr. kaufmann' in text.lower():
        event['title'] = 'Termin bei Dr. Kaufmann'
        event['category'] = 'Termin'
        # Aus der Payload: "Heute um 16:30 Uhr"
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*uhr', text.lower())
        if time_match:
            event['time'] = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"
        
        # Datum aus dem Schedule
        if schedule.get('kind') == 'at':
            at_str = schedule.get('at', '')
            # 2026-03-26T07:00:00.000Z -> Erinnerung war 08:00, Termin ist 16:30
            try:
                dt = datetime.fromisoformat(at_str.replace('Z', '+00:00'))
                # Termin ist am selben Tag, aber um 16:30
                event['date'] = dt.strftime('%Y-%m-%d')
                event['reminder_minutes'] = 540  # 9 Stunden vorher (08:00 vs 16:30)
            except:
                pass
    
    # Geburtstage
    elif 'geburtstag' in text.lower():
        # Extrahiere Name
        name_match = re.search(r'(?:heute ist|heute hat)\s+(\w+)\s+geburtstag', text.lower())
        if name_match:
            person = name_match.group(1).capitalize()
            event['title'] = f'Geburtstag {person}'
            event['category'] = 'Geburtstag'
            event['recurrence'] = 'yearly'
        else:
            event['title'] = 'Geburtstag'
            event['category'] = 'Geburtstag'
            event['recurrence'] = 'yearly'
        
        # Extrahiere Name aus dem Job-Namen
        if 'sepp' in name.lower():
            event['title'] = 'Geburtstag Sepp'
        elif 'doris' in name.lower():
            event['title'] = 'Geburtstag Doris'
        elif 'jasmin' in name.lower():
            event['title'] = 'Geburtstag Jasmin'
        elif 'dennis' in name.lower():
            event['title'] = 'Geburtstag Dennis'
        
        # Datum aus dem Schedule
        if schedule.get('kind') == 'at':
            at_str = schedule.get('at', '')
            try:
                dt = datetime.fromisoformat(at_str.replace('Z', '+00:00'))
                event['date'] = dt.strftime('%Y-%m-%d')
                event['time'] = '06:00'  # Erinnerung um 06:00
                event['reminder_minutes'] = 0  # Zur Erinnerungszeit
            except:
                pass
    
    # Nur Events mit Datum zurückgeben
    if event['date']:
        return event
    return None

def import_events():
    """Importiert alle gefundenen Events."""
    
    print("🎩 OpenClaw Calendar - Import Tool\n")
    print("Suche nach bestehenden Terminen in Cron-Jobs...\n")
    
    events = parse_cron_jobs()
    
    if not events:
        print("❌ Keine importierbaren Termine gefunden.")
        return
    
    print(f"✅ {len(events)} Termine gefunden:\n")
    
    cal = Calendar()
    imported = 0
    
    for event in events:
        print(f"📅 {event['date']}", end="")
        if event['time']:
            print(f" {event['time']}", end="")
        print(f" - {event['title']}")
        
        if event['recurrence'] != 'none':
            print(f"   🔄 {event['recurrence']}")
        if event['reminder_minutes']:
            print(f"   ⏰ Erinnerung: {event['reminder_minutes']} Minuten vorher")
        
        # Speichern
        try:
            event_id = cal.add_event(
                title=event['title'],
                date=event['date'],
                time=event['time'],
                description='',
                category=event['category'],
                recurrence=event['recurrence'],
                reminder_minutes=event['reminder_minutes']
            )
            print(f"   ✅ Importiert (ID: {event_id})\n")
            imported += 1
        except Exception as e:
            print(f"   ❌ Fehler: {e}\n")
    
    print(f"\n{'='*50}")
    print(f"✅ {imported}/{len(events)} Termine erfolgreich importiert!")
    print(f"{'='*50}\n")
    
    print("Nächste Schritte:")
    print("1. Cron-Jobs synchronisieren: python3 calendar_cli.py --sync-crons")
    print("2. Alte Cron-Jobs manuell aus jobs.json entfernen (optional)")
    print("3. Termine anzeigen: python3 calendar_cli.py --upcoming")

if __name__ == '__main__':
    import_events()
