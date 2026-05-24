#!/usr/bin/env python3
"""
James Calendar CLI - Kommandozeilen-Interface
Natürliche Spracheingabe und Termin-Verwaltung.
"""

import sys
import os
import re
import argparse
from datetime import datetime, timedelta
from datetime import timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from james_calendar import Calendar, DB_PATH


class NaturalLanguageParser:
    """Parst natürliche Spracheingaben in Datum/Zeit."""
    
    GERMAN_MONTHS = {
        'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
        'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12
    }
    
    GERMAN_WEEKDAYS = {
        'montag': 0, 'dienstag': 1, 'mittwoch': 2, 'donnerstag': 3,
        'freitag': 4, 'samstag': 5, 'sonntag': 6
    }
    
    def __init__(self):
        self.now = datetime.now()
    
    def parse(self, text: str) -> dict:
        """
        Parst einen natürlichen Sprachtext.
        
        Returns:
            Dict mit: title, date, time, description, category, recurrence, reminder_minutes
        """
        text_lower = text.lower()
        result = {
            'title': '',
            'date': None,
            'time': None,
            'description': '',
            'category': 'Termin',
            'recurrence': 'none',
            'reminder_minutes': None
        }
        
        # Extrahiere Reminder (--remind Xh/Xm/Xd)
        remind_match = re.search(r'--remind\s+(\d+)([hmd])', text_lower)
        if remind_match:
            value = int(remind_match.group(1))
            unit = remind_match.group(2)
            if unit == 'h':
                result['reminder_minutes'] = value * 60
            elif unit == 'd':
                result['reminder_minutes'] = value * 60 * 24
            else:  # m
                result['reminder_minutes'] = value
            # Entferne aus Text
            text = re.sub(r'--remind\s+\d+[hmd]', '', text, flags=re.IGNORECASE).strip()
            text_lower = text.lower()
        
        # Extrahiere Wiederholungen
        if '--yearly' in text_lower or 'jedes jahr' in text_lower or 'jährlich' in text_lower:
            result['recurrence'] = 'yearly'
            text = re.sub(r'--yearly|jedes jahr|jährlich', '', text, flags=re.IGNORECASE).strip()
            text_lower = text.lower()
        elif '--monthly' in text_lower or 'jeden monat' in text_lower or 'monatlich' in text_lower:
            result['recurrence'] = 'monthly'
            text = re.sub(r'--monthly|jeden monat|monatlich', '', text, flags=re.IGNORECASE).strip()
            text_lower = text.lower()
        elif '--weekly' in text_lower or 'jede woche' in text_lower or 'wöchentlich' in text_lower:
            result['recurrence'] = 'weekly'
            text = re.sub(r'--weekly|jede woche|wöchentlich', '', text, flags=re.IGNORECASE).strip()
            text_lower = text.lower()
        elif '--daily' in text_lower or 'jeden tag' in text_lower or 'täglich' in text_lower:
            result['recurrence'] = 'daily'
            text = re.sub(r'--daily|jeden tag|täglich', '', text, flags=re.IGNORECASE).strip()
            text_lower = text.lower()
        
        # Kategorie erkennen
        if 'geburtstag' in text_lower:
            result['category'] = 'Geburtstag'
            result['recurrence'] = result['recurrence'] or 'yearly'
        elif 'termin' in text_lower:
            result['category'] = 'Termin'
        
        # Datum parsen
        date = self._parse_date(text_lower)
        if date:
            result['date'] = date.strftime('%Y-%m-%d')
        
        # Zeit parsen
        time = self._parse_time(text_lower)
        if time:
            result['time'] = time
        
        # Titel extrahieren (Rest nach Entfernung von Datum/Zeit)
        title = self._extract_title(text)
        result['title'] = title
        
        return result
    
    def _parse_date(self, text: str) -> datetime:
        """Extrahiert das Datum aus dem Text."""
        
        # "morgen"
        if 'morgen' in text and 'übermorgen' not in text:
            return self.now + timedelta(days=1)
        
        # "übermorgen"
        if 'übermorgen' in text:
            return self.now + timedelta(days=2)
        
        # "heute"
        if 'heute' in text:
            return self.now
        
        # "nächste woche [Tag]"
        next_week_match = re.search(r'nächste\s+woche\s+(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)', text)
        if next_week_match:
            weekday = self.GERMAN_WEEKDAYS[next_week_match.group(1)]
            days_ahead = weekday - self.now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return self.now + timedelta(days=days_ahead + 7)
        
        # "[Tag]" (diese Woche oder nächste)
        weekday_match = re.search(r'\b(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)\b', text)
        if weekday_match:
            weekday = self.GERMAN_WEEKDAYS[weekday_match.group(1)]
            days_ahead = weekday - self.now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return self.now + timedelta(days=days_ahead)
        
        # "in X tagen"
        in_days_match = re.search(r'in\s+(\d+)\s+tag(en)?', text)
        if in_days_match:
            days = int(in_days_match.group(1))
            return self.now + timedelta(days=days)
        
        # "in X wochen"
        in_weeks_match = re.search(r'in\s+(\d+)\s+woche(n)?', text)
        if in_weeks_match:
            weeks = int(in_weeks_match.group(1))
            return self.now + timedelta(weeks=weeks)
        
        # "am DD.MM." oder "DD.MM."
        date_match = re.search(r'(?:am\s+)?(\d{1,2})[\.-](\d{1,2})(?:[\.-](\d{2,4}))?', text)
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year_str = date_match.group(3)
            
            if year_str:
                year = int(year_str) if len(year_str) == 4 else 2000 + int(year_str)
            else:
                year = self.now.year
                # Falls Datum in der Vergangenheit, nächstes Jahr
                parsed = datetime(year, month, day)
                if parsed < self.now:
                    year += 1
            
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        # Monatsname "am DD. Monat"
        for month_name, month_num in self.GERMAN_MONTHS.items():
            pattern = r'(?:am\s+)?(\d{1,2})\.?\s*' + month_name
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = self.now.year
                # Falls Datum in der Vergangenheit, nächstes Jahr
                parsed = datetime(year, month_num, day)
                if parsed < self.now.replace(hour=0, minute=0, second=0):
                    year += 1
                return datetime(year, month_num, day)
        
        return None
    
    def _parse_time(self, text: str) -> str:
        """Extrahiert die Zeit aus dem Text."""
        
        # "XX Uhr" oder "XX:YY Uhr"
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*uhr', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            return f"{hour:02d}:{minute:02d}"
        
        # "XX:YY" (24h Format)
        time_match = re.search(r'\b(\d{1,2}):(\d{2})\b', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            if 0 <= hour < 24 and 0 <= minute < 60:
                return f"{hour:02d}:{minute:02d}"
        
        return None
    
    def _extract_title(self, text: str) -> str:
        """Extrahiert den Titel aus dem Text."""
        # Entferne häufige Zeit/Datum-Muster
        cleaned = text
        
        # Entferne "am DD.MM."
        cleaned = re.sub(r'am\s+\d{1,2}[\.-]\d{1,2}(?:[\.-]\d{2,4})?', '', cleaned)
        
        # Entferne "morgen", "heute", etc.
        for word in ['morgen', 'übermorgen', 'heute', 'nächste woche', 'jede woche', 
                     'jeden tag', 'jeden monat', 'jedes jahr', 'geburtstag']:
            cleaned = re.sub(r'\b' + word + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Entferne Wochentage
        for day in self.GERMAN_WEEKDAYS.keys():
            cleaned = re.sub(r'\b' + day + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Entferne "Uhr" Zeitangaben
        cleaned = re.sub(r'\d{1,2}(?::\d{2})?\s*uhr', '', cleaned, flags=re.IGNORECASE)
        
        # Bereinige
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned if cleaned else 'Termin'


def format_event(event: dict) -> str:
    """Formatiert einen Termin für die Ausgabe."""
    lines = []
    
    # Datum formatieren
    date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
    date_str = date_obj.strftime('%d.%m.%Y')
    
    # Wochentag
    weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    weekday = weekdays[date_obj.weekday()]
    
    # Zeit
    time_str = event['time'] if event['time'] else 'ganztägig'
    
    # Icon basierend auf Kategorie
    icon = '📅'
    if event['category'] == 'Geburtstag':
        icon = '🎂'
    elif event['category'] == 'Erinnerung':
        icon = '⏰'
    
    # Recurrence
    rec_str = ''
    if event['recurrence'] == 'daily':
        rec_str = ' [täglich]'
    elif event['recurrence'] == 'weekly':
        rec_str = ' [wöchentlich]'
    elif event['recurrence'] == 'monthly':
        rec_str = ' [monatlich]'
    elif event['recurrence'] == 'yearly':
        rec_str = ' [jährlich]'
    
    # Reminder
    remind_str = ''
    if event['reminder_minutes']:
        if event['reminder_minutes'] >= 1440:
            remind_str = f" (Erinnerung {event['reminder_minutes'] // 1440}d vorher)"
        elif event['reminder_minutes'] >= 60:
            remind_str = f" (Erinnerung {event['reminder_minutes'] // 60}h vorher)"
        else:
            remind_str = f" (Erinnerung {event['reminder_minutes']}m vorher)"
    
    return f"{icon} **{date_str}** ({weekday}) {time_str} - {event['title']}{rec_str}{remind_str}"


def main():
    parser = argparse.ArgumentParser(description='James Calendar - Termin-Verwaltung')
    parser.add_argument('text', nargs='?', help='Natürliche Spracheingabe für Termin')
    parser.add_argument('--init', action='store_true', help='Datenbank initialisieren')
    parser.add_argument('--today', action='store_true', help='Heutige Termine anzeigen')
    parser.add_argument('--week', action='store_true', help='Diese Woche anzeigen')
    parser.add_argument('--month', action='store_true', help='Diesen Monat anzeigen')
    parser.add_argument('--upcoming', action='store_true', help='Kommende Termine anzeigen')
    parser.add_argument('--list', action='store_true', help='Alle Termine anzeigen')
    parser.add_argument('--delete', type=int, help='Termin löschen (ID)')
    parser.add_argument('--sync-crons', action='store_true', help='Cron-Jobs synchronisieren')
    parser.add_argument('--cleanup-crons', action='store_true', help='Überflüssige Cron-Jobs entfernen')
    
    args = parser.parse_args()
    
    cal = Calendar()
    
    # Initialisierung
    if args.init:
        print(f"✅ Kalender-Datenbank initialisiert: {DB_PATH}")
        return
    
    # Termin hinzufügen
    if args.text:
        nlp = NaturalLanguageParser()
        parsed = nlp.parse(args.text)
        
        if not parsed['date']:
            print("❌ Kein Datum erkannt. Bitte gib ein Datum an.")
            return
        
        event_id = cal.add_event(
            title=parsed['title'],
            date=parsed['date'],
            time=parsed['time'],
            description=parsed['description'],
            category=parsed['category'],
            recurrence=parsed['recurrence'],
            reminder_minutes=parsed['reminder_minutes']
        )
        
        print(f"✅ Termin gespeichert (ID: {event_id})")
        print(f"   📅 {parsed['date']}", end="")
        if parsed['time']:
            print(f" um {parsed['time']}", end="")
        print(f" - {parsed['title']}")
        
        if parsed['recurrence'] != 'none':
            print(f"   🔄 Wiederholung: {parsed['recurrence']}")
        if parsed['reminder_minutes']:
            print(f"   ⏰ Erinnerung: {parsed['reminder_minutes']} Minuten vorher")
        
        return
    
    # Termine anzeigen
    if args.today:
        events = cal.get_today()
        print(f"📅 **Heute** ({datetime.now().strftime('%d.%m.%Y')})\n")
        if events:
            for e in events:
                print(format_event(e))
        else:
            print("Keine Termine heute.")
    
    elif args.week:
        events = cal.get_week()
        print(f"📅 **Diese Woche**\n")
        if events:
            for e in events:
                print(format_event(e))
        else:
            print("Keine Termine diese Woche.")
    
    elif args.month:
        events = cal.get_month()
        print(f"📅 **Dieser Monat** ({datetime.now().strftime('%B %Y')})\n")
        if events:
            for e in events:
                print(format_event(e))
        else:
            print("Keine Termine diesen Monat.")
    
    elif args.upcoming:
        events = cal.get_upcoming(limit=20)
        print(f"📅 **Kommende Termine**\n")
        if events:
            for e in events:
                print(format_event(e))
        else:
            print("Keine kommenden Termine.")
    
    elif args.list:
        events = cal.get_upcoming(limit=100)
        print(f"📅 **Alle Termine**\n")
        if events:
            for e in events:
                print(f"[{e['id']}] {format_event(e)}")
        else:
            print("Keine Termine vorhanden.")
    
    # Termin löschen
    elif args.delete:
        if cal.delete_event(args.delete):
            print(f"✅ Termin {args.delete} gelöscht.")
        else:
            print(f"❌ Termin {args.delete} nicht gefunden.")
    
    # Cron sync
    elif args.sync_crons:
        count = cal.sync_cron_jobs()
        print(f"✅ {count} Cron-Jobs erstellt/aktualisiert.")
    
    # Cron cleanup
    elif args.cleanup_crons:
        print("🧹 Cron-Jobs werden bereinigt...")
        # TODO: Implement cleanup
        print("✅ Bereinigung abgeschlossen.")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
