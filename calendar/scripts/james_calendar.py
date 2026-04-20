#!/usr/bin/env python3
"""
OpenClaw Calendar - Hauptmodul
SQLite-basierter Kalender mit natürlicher Spracheingabe und Cron-Integration.
"""

import sqlite3
import json
import re
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


DB_PATH = os.path.expanduser("~/.openclaw/workspace/data/calendar.db")
CRON_JOBS_FILE = os.path.expanduser("~/.openclaw/workspace/cron/jobs.json")


class Calendar:
    """Hauptklasse für den OpenClaw Calendar."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """Stellt sicher, dass die Datenbank existiert."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT,
                    description TEXT,
                    category TEXT DEFAULT 'Termin',
                    recurrence TEXT DEFAULT 'none',
                    reminder_minutes INTEGER,
                    cron_job_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS cron_links (
                    event_id INTEGER NOT NULL,
                    cron_job_id TEXT NOT NULL,
                    notify_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (event_id, cron_job_id),
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
                CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
            ''')
    
    def add_event(self, title: str, date: str, time: Optional[str] = None,
                  description: str = "", category: str = "Termin",
                  recurrence: str = "none", reminder_minutes: Optional[int] = None) -> int:
        """
        Fügt einen neuen Termin hinzu.
        
        Args:
            title: Bezeichnung des Termins
            date: Datum im Format YYYY-MM-DD
            time: Optional Zeit im Format HH:MM
            description: Optionale Beschreibung
            category: Termin, Geburtstag, oder Erinnerung
            recurrence: none, daily, weekly, monthly, yearly
            reminder_minutes: Minuten vorher für Erinnerung
            
        Returns:
            Die ID des neuen Events
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO events (title, date, time, description, category, recurrence, reminder_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, date, time, description, category, recurrence, reminder_minutes))
            event_id = cursor.lastrowid
            
            conn.commit()
            
        # Cron-Job erstellen falls Erinnerung gewünscht (außerhalb des DB-Contexts)
        if reminder_minutes:
            self._create_reminder_cron(event_id, title, date, time, reminder_minutes, recurrence)
            
            return event_id
    
    def _create_reminder_cron(self, event_id: int, title: str, date: str, 
                               time: Optional[str], reminder_minutes: int, recurrence: str):
        """Erstellt einen Cron-Job für die Erinnerung."""
        
        # Berechne Erinnerungszeit
        event_dt = datetime.strptime(f"{date} {time or '00:00'}", "%Y-%m-%d %H:%M")
        reminder_dt = event_dt - timedelta(minutes=reminder_minutes)
        
        # Topic 12 für Termine/Geburtstage
        topic_id = "-1003765464477:12"
        
        if recurrence == "yearly":
            # Für Geburtstage: jährlich wiederholend
            cron_expr = f"{reminder_dt.minute} {reminder_dt.hour} {event_dt.day} {event_dt.month} *"
            schedule = {"kind": "cron", "expr": cron_expr, "tz": "Europe/Berlin"}
        elif recurrence == "weekly":
            # Wöchentlich
            weekday = event_dt.strftime("%w")  # 0=Sonntag
            cron_expr = f"{reminder_dt.minute} {reminder_dt.hour} * * {weekday}"
            schedule = {"kind": "cron", "expr": cron_expr, "tz": "Europe/Berlin"}
        elif recurrence == "monthly":
            # Monatlich
            cron_expr = f"{reminder_dt.minute} {reminder_dt.hour} {event_dt.day} * *"
            schedule = {"kind": "cron", "expr": cron_expr, "tz": "Europe/Berlin"}
        elif recurrence == "daily":
            # Täglich
            cron_expr = f"{reminder_dt.minute} {reminder_dt.hour} * * *"
            schedule = {"kind": "cron", "expr": cron_expr, "tz": "Europe/Berlin"}
        else:
            # Einmalig
            schedule = {
                "kind": "at",
                "at": reminder_dt.strftime("%Y-%m-%dT%H:%M:00.000Z")
            }
        
        # Cron-Job erstellen
        cron_job = {
            "id": f"calendar-{event_id}-{int(datetime.now().timestamp())}",
            "agentId": "main",
            "sessionKey": "agent:main:telegram:group:-1003765464477:topic:12",
            "name": f"Kalender: {title}",
            "enabled": True,
            "schedule": schedule,
            "sessionTarget": "main",
            "wakeMode": "now",
            "deleteAfterRun": recurrence == "none",  # Einmalige werden gelöscht
            "payload": {
                "kind": "systemEvent",
                "text": f"CRON_CALENDAR_REMINDER: Event ID {event_id} - {title} am {date} um {time or 'ganztägig'}. Poste in Telegram Topic 12 ({topic_id})."
            }
        }
        
        # Zu Cron-Jobs hinzufügen
        self._save_cron_job(cron_job)
        
        # Link speichern
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO cron_links (event_id, cron_job_id, notify_at)
                VALUES (?, ?, ?)
            ''', (event_id, cron_job["id"], reminder_dt.isoformat()))
    
    def _save_cron_job(self, job: Dict):
        """Speichert einen Cron-Job in der jobs.json."""
        try:
            with open(CRON_JOBS_FILE, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"version": 1, "jobs": []}
        
        # Füge State hinzu
        job["state"] = {
            "nextRunAtMs": None,
            "lastRunAtMs": None,
            "lastRunStatus": None,
            "lastStatus": "pending"
        }
        
        # Füge Timestamps hinzu
        now = int(datetime.now().timestamp() * 1000)
        job["createdAtMs"] = now
        job["updatedAtMs"] = now
        
        data["jobs"].append(job)
        
        with open(CRON_JOBS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_today(self) -> List[Dict]:
        """Gibt alle Termine für heute zurück."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self._get_events_for_date(today)
    
    def get_week(self) -> List[Dict]:
        """Gibt alle Termine für diese Woche zurück."""
        today = datetime.now()
        start = today - timedelta(days=today.weekday())  # Montag
        end = start + timedelta(days=6)  # Sonntag
        
        return self._get_events_between(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def get_month(self) -> List[Dict]:
        """Gibt alle Termine für diesen Monat zurück."""
        today = datetime.now()
        start = today.replace(day=1)
        # Ende des Monats: nächster Monat, Tag 1, minus 1 Tag
        if today.month == 12:
            next_month = start.replace(year=today.year + 1, month=1)
        else:
            next_month = start.replace(month=today.month + 1)
        end = next_month - timedelta(days=1)
        
        return self._get_events_between(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def get_upcoming(self, limit: int = 20) -> List[Dict]:
        """Gibt kommende Termine zurück."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE date >= ? 
                ORDER BY date, time
                LIMIT ?
            ''', (today, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def _get_events_for_date(self, date: str) -> List[Dict]:
        """Holt Termine für ein bestimmtes Datum."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE date = ? 
                ORDER BY time
            ''', (date,))
            return [dict(row) for row in cursor.fetchall()]
    
    def _get_events_between(self, start: str, end: str) -> List[Dict]:
        """Holt Termine zwischen zwei Daten."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE date BETWEEN ? AND ? 
                ORDER BY date, time
            ''', (start, end))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_event(self, event_id: int) -> bool:
        """Löscht einen Termin und seinen Cron-Job."""
        with sqlite3.connect(self.db_path) as conn:
            # Hole Cron-Job IDs
            cursor = conn.execute('SELECT cron_job_id FROM cron_links WHERE event_id = ?', (event_id,))
            cron_ids = [row[0] for row in cursor.fetchall()]
            
            # Lösche aus DB (cascade löscht auch cron_links)
            conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
            
            # Lösche Cron-Jobs
            for cron_id in cron_ids:
                self._delete_cron_job(cron_id)
            
            return True
    
    def _delete_cron_job(self, cron_job_id: str):
        """Löscht einen Cron-Job aus der jobs.json."""
        try:
            with open(CRON_JOBS_FILE, 'r') as f:
                data = json.load(f)
            
            data["jobs"] = [j for j in data["jobs"] if j.get("id") != cron_job_id]
            
            with open(CRON_JOBS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warnung: Konnte Cron-Job nicht löschen: {e}")
    
    def sync_cron_jobs(self):
        """Synchronisiert alle Erinnerungen mit Cron-Jobs."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE reminder_minutes IS NOT NULL 
                AND cron_job_id IS NULL
            ''')
            events = [dict(row) for row in cursor.fetchall()]
        
        for event in events:
            self._create_reminder_cron(
                event["id"],
                event["title"],
                event["date"],
                event["time"],
                event["reminder_minutes"],
                event["recurrence"]
            )
        
        return len(events)


if __name__ == "__main__":
    # Test
    cal = Calendar()
    print(f"Calendar initialisiert. DB: {DB_PATH}")
