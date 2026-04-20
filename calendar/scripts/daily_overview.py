#!/usr/bin/env python3
"""
Täglicher Termin-Überblick für OpenClaw Calendar
Postet alle Termine des Tages um 08:00 Uhr in Topic 12.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_calendar import Calendar

def get_daily_overview():
    """Holt den täglichen Termin-Überblick."""
    cal = Calendar()
    events = cal.get_today()
    
    if not events:
        return None
    
    lines = []
    lines.append("📅 **Termine heute**\n")
    
    for event in events:
        icon = '🎂' if event['category'] == 'Geburtstag' else '📅'
        time_str = event['time'] if event['time'] else 'ganztägig'
        
        lines.append(f"{icon} {time_str} - {event['title']}")
        
        if event['recurrence'] != 'none':
            rec_map = {'daily': 'täglich', 'weekly': 'wöchentlich', 
                      'monthly': 'monatlich', 'yearly': 'jährlich'}
            lines.append(f"   🔄 {rec_map.get(event['recurrence'], event['recurrence'])}")
    
    return "\n".join(lines)

if __name__ == '__main__':
    overview = get_daily_overview()
    if overview:
        print(overview)
    else:
        print("NO_EVENTS")
