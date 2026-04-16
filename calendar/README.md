# calendar

# Calendar Skill - James Calendar

Ein schlanker, lokaler Kalender für OpenClaw mit SQLite-Backend und natürlicher Spracheingabe.

## Features

- 📝 **Natürliche Spracheingabe**: *"Termin morgen 14 Uhr mit Dr. Kaufmann"*
- 🎂 **Geburtstage**: Automatische jährliche Erinnerungen
- ⏰ **Erinnerungen**: Flexible Vorlaufzeiten (Minuten, Stunden, Tage)
- 🔁 **Wiederholungen**: Täglich, wöchentlich, monatlich, jährlich
- 📅 **Übersichten**: Tages-, Wochen-, Monatsansicht
- 💾 **SQLite**: Lokale Datenbank, keine Cloud-Abhängigkeit
- 🤖 **Cron-Integration**: Automatische Cron-Job-Erstellung für Erinnerungen

## Schnellstart

### Datenbank initialisieren
```bash
python3 skills/calendar/scripts/calendar_cli.py --init
```

### Termin hinzufügen
```bash
# Per Text
python3 skills/calendar/scripts/calendar_cli.py "Termin morgen 14 Uhr mit Dr. Kaufmann"
python3 skills/calendar/scripts/calendar_cli.py "Geburtstag Sepp am 31.03."
python3 skills/calendar/scripts/calendar_cli.py "Meeting jeden Montag 9 Uhr"

# Mit Erinnerung
python3 skills/calendar/scripts/calendar_cli.py "Zahnarzt am 15.04. um 10 Uhr --remind 1h"
```

### Termine anzeigen
```bash
# Heute
python3 skills/calendar/scripts/calendar_cli.py --today

# Diese Woche
python3 skills/calendar/scripts/calendar_cli.py --week

# Diesen Monat
python3 skills/calendar/scripts/calendar_cli.py --month

# Alle kommenden
python3 skills/calendar/scripts/calendar_cli.py --upcoming
```

### Cron-Jobs verwalten
```bash
# Alle Erinnerungen als Cron-Jobs erstellen
python3 skills/calendar/scripts/calendar_cli.py --sync-crons

# Überfällige/alte Cron-Jobs aufräumen
python3 skills/calendar/scripts/calendar_cli.py --cleanup-crons
```

## Datenbank-Schema

**Tabelle `events`:**
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| title | TEXT | Termin-Bezeichnung |
| date | TEXT | ISO-8601 Datum (YYYY-MM-DD) |
| time | TEXT | Zeit (HH:MM) oder NULL |
| description | TEXT | Optional: Details |
| category | TEXT | Termin/Geburtstag/Erinnerung |
| recurrence | TEXT | none/daily/weekly/monthly/yearly |
| reminder_minutes | INTEGER | Minuten vorher (NULL = keine) |
| cron_job_id | TEXT | Verknüpfter Cron-Job (optional) |
| created_at | TEXT | Timestamp |

**Tabelle `cron_links`:**
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| event_id | INTEGER | Referenz zu events |
| cron_job_id | TEXT | OpenClaw Cron-Job ID |
| notify_at | TEXT | ISO-8601 Zeitpunkt |

## Natürliche Spracheingabe

### Unterstützte Muster

| Eingabe | Erkannt als |
|---------|-------------|
| "morgen 14 Uhr" | Datum: morgen, Zeit: 14:00 |
| "übermorgen" | Datum: +2 Tage |
| "nächste Woche Dienstag" | Datum: nächster Dienstag |
| "am 15.04." | Datum: 15.04. (aktuelles Jahr) |
| "jeden Montag" | Wöchentliche Wiederholung |
| "monatlich am 1." | Monatliche Wiederholung |
| "jährlich am 31.03." | Jährliche Wiederholung |
| "in 30 Minuten" | Relativer Zeitpunkt |
| "--remind 1h" | 1 Stunde vorher erinnern |
| "--remind 30m" | 30 Minuten vorher erinnern |
| "--remind 1d" | 1 Tag vorher erinnern |

### Beispiele

```bash
# Einzeltermin
"Meeting mit Team morgen 15 Uhr"

# Mit Erinnerung
"Zahnarzt am 20.04. 10 Uhr --remind 2h"

# Geburtstag (jährlich wiederholend)
"Geburtstag Sepp am 31.03. --yearly"

# Wöchentlich
"Sport jeden Mittwoch 18 Uhr --weekly --remind 30m"

# Täglich
"Medikament einnehmen jeden Tag 8 Uhr --daily"
```

## Cron-Integration

Der Skill erstellt automatisch Cron-Jobs für Erinnerungen:

- **Einmalige Termine**: Cron mit `schedule.kind: "at"` + `deleteAfterRun: true`
- **Wiederholende Termine**: Cron mit `schedule.kind: "cron"` Expression
- **Geburtstage**: Automatisch jährlich wiederholend

**Format der Cron-Nachricht:**
```
CRON_CALENDAR_REMINDER: Event ID {id} - {title} um {time}
```

## API in Python nutzen

```python
from skills.calendar.scripts.calendar import Calendar

cal = Calendar()

# Termin hinzufügen
event_id = cal.add_event(
    title="Meeting mit Team",
    date="2026-04-15",
    time="14:00",
    description="Wöchentliches Team-Meeting",
    recurrence="weekly",
    reminder_minutes=30
)

# Termine abrufen
today = cal.get_today()
this_week = cal.get_week()
upcoming = cal.get_upcoming(limit=10)

# Cron sync
cal.sync_cron_jobs()
```

## Backup

Die Datenbank liegt unter:
```
~/.openclaw/workspace/data/calendar.db
```

Wird automatisch mit dem täglichen Git+SQLite Backup gesichert.

## Automatische Eintragung durch James

**WICHTIGE REGEL:** Wenn Eure Lordschaft folgende Begriffe verwendet, trage ich automatisch in den Kalender ein:

| Begriff | Beispiel | Aktion |
|---------|----------|--------|
| **Termin** | "Termin bei Dr. Riedl Dienstag 17 Uhr" | Automatisch eintragen mit Erinnerung |
| **Geburtstag** | "Geburtstag Sepp am 31.03." | Automatisch eintragen (jährlich wiederholend) |
| **Ereignis** | "Ereignis: Prüfung am 15.05." | Automatisch eintragen |
| **Erinnerung** | "Erinnerung: Rechnung zahlen morgen" | Automatisch eintragen |

**Standard-Einstellungen:**
- Erinnerung: 8 Stunden vorher (außer anders gewünscht)
- Geburtstage: Jährlich wiederholend
- Ausgabe: Bestätigung der Eintragung

**Täglicher Überblick:**
- 07:45 Uhr: Prüfung auf Termine des Tages
- Post in Topic 12 bei Terminen
- Absolute Stille bei leeren Tagen

---
*Erstellt für Eure Lordschaft* 🎩
