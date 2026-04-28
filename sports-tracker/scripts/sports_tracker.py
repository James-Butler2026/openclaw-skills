#!/usr/bin/env python3
"""
Sports Tracker v2.0
P90X, Spazieren und Fahrrad-Tracking mit SQLite, Workouts & Kalorien-Berechnung
"""

import os
import sys
import re
import sqlite3
import argparse
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("/home/node/.openclaw/workspace/data/sports_tracker.db")

CATEGORIES = ["P90X", "Spazieren", "Fahrrad"]

# MET-Werte für Kalorienberechnung
MET_VALUES = {
    "Fahrrad": 8.0,
    "Spazieren": 3.5,
    "P90X": 6.0,
}

# Durchschnittsgeschwindigkeiten (km/h) für Dauerberechnung
SPEED_KMH = {
    "Fahrrad": 18.0,
    "Spazieren": 4.5,
}

# P90X Standard-Dauer (Minuten)
P90X_DEFAULT_DURATION = 60

# Sarkasmus-Texte (3 verschiedene, zufällig)
SARCASM_LINES = [
    "🎩 *räuspert sich* Die Lordschaft scheint die noble Kunst des ... Ausruhens zu pflegen.",
    "💀 Oh, Sie haben also DOCH ein Hobby außer Couch-Drücken? Beeindruckend.",
    "🏆 *holt tief Luft* Soll ich den Pokal für 'Beste Ausrede' holen, oder trainieren wir heute?",
]

# Mapping Wochentag → Trainings-Flag (Python: Mo=0, Di=1, Mi=2, Do=3, Fr=4, Sa=5, So=6)
TRAINING_DAYS = {0, 2, 4}  # Montag, Mittwoch, Freitag
REST_DAYS = {1, 3, 5, 6}   # Dienstag, Donnerstag, Samstag, Sonntag


def _get_conn():
    """Hilfsfunktion für DB-Verbindung mit Foreign Keys"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _get_weight():
    """Liest aktuelles Gewicht aus user_settings"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_settings WHERE key = 'weight_kg'")
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row else 120.0


def _set_weight(kg):
    """Aktualisiert Gewicht"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_settings (key, value) VALUES ('weight_kg', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (str(kg),)
    )
    conn.commit()
    conn.close()


def _calculate_calories(category, km_or_done, duration_min=None, weight_kg=None):
    """
    Berechnet Kalorien basierend auf MET-Wert, Gewicht und Dauer.
    Formel: Kcal = MET * Gewicht_kg * Dauer_h
    """
    if weight_kg is None:
        weight_kg = _get_weight()

    met = MET_VALUES.get(category, 3.5)

    if category in ("Fahrrad", "Spazieren"):
        # Bei km-basierten Aktivitäten: Dauer aus km / Geschwindigkeit
        try:
            km = float(str(km_or_done).replace(",", "."))
        except (ValueError, TypeError):
            km = 0.0
        speed = SPEED_KMH.get(category, 5.0)
        duration_h = km / speed if speed > 0 else 0
        duration_min = int(duration_h * 60)
        calories = int(met * weight_kg * duration_h)
        return calories, duration_min, speed

    elif category == "P90X":
        # P90X: Standard 60 min, oder optional angegeben
        if duration_min is None:
            duration_min = P90X_DEFAULT_DURATION
        duration_h = duration_min / 60.0
        calories = int(met * weight_kg * duration_h)
        return calories, duration_min, None

    return 0, 0, None


def _migrate_v1_to_v2():
    """Migriert bestehende DB von v1 auf v2 (neue Spalten + Tabellen)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Prüfe ob activities.type existiert (Marker für v2)
    cursor.execute("PRAGMA table_info(activities)")
    cols = [row[1] for row in cursor.fetchall()]

    if "type" not in cols:
        cursor.execute("ALTER TABLE activities ADD COLUMN type TEXT DEFAULT 'cardio'")
    if "duration_min" not in cols:
        cursor.execute("ALTER TABLE activities ADD COLUMN duration_min INTEGER")
    if "calories" not in cols:
        cursor.execute("ALTER TABLE activities ADD COLUMN calories INTEGER")
    if "speed_kmh" not in cols:
        cursor.execute("ALTER TABLE activities ADD COLUMN speed_kmh REAL")
    if "weight_kg" not in cols:
        cursor.execute("ALTER TABLE activities ADD COLUMN weight_kg REAL DEFAULT 120")

    # user_settings Tabelle (key/value Store)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # Prüfe ob altes id/weight_kg Schema existiert
    cursor.execute("PRAGMA table_info(user_settings)")
    us_cols = [row[1] for row in cursor.fetchall()]
    if "id" in us_cols:
        # Altes Schema: Tabelle neu erstellen
        cursor.execute("DROP TABLE user_settings")
        cursor.execute("""
            CREATE TABLE user_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
    # Standardwerte einfügen
    cursor.execute("INSERT OR IGNORE INTO user_settings (key, value) VALUES ('weight_kg', '120')")
    cursor.execute("INSERT OR IGNORE INTO user_settings (key, value) VALUES ('training_days', '1,3,5')")
    cursor.execute("INSERT OR IGNORE INTO user_settings (key, value) VALUES ('sarcasm_threshold', '2')")

    # workout_rules Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_rules (
            id INTEGER PRIMARY KEY,
            training_days TEXT DEFAULT '1,3,5',
            sarcasm_threshold INTEGER DEFAULT 2
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO workout_rules (id, training_days, sarcasm_threshold) VALUES (1, '1,3,5', 2)")

    # workout_status Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_status (
            id INTEGER PRIMARY KEY,
            date TEXT UNIQUE NOT NULL,
            is_training_day BOOLEAN,
            status TEXT,
            type TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_workout_date ON workout_status(date)")

    conn.commit()
    conn.close()


def init_db():
    """Initialisiert oder migriert die Datenbank"""
    is_new = not DB_PATH.exists()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            value TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            type TEXT DEFAULT 'cardio',
            duration_min INTEGER,
            calories INTEGER,
            speed_kmh REAL,
            weight_kg REAL DEFAULT 120
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON activities(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON activities(category)")

    conn.commit()
    conn.close()

    # Migration (neue Spalten + Tabellen)
    _migrate_v1_to_v2()

    if is_new:
        print(f"✅ Datenbank initialisiert: {DB_PATH}")
        seed_data()
        return True
    else:
        print("✅ Datenbank bereits vorhanden – Migration auf v2 durchgeführt.")
        return False


def parse_date(text):
    """Erkennt deutsche Datumsangaben"""
    text_lower = text.lower()
    today = datetime.now()

    if "vorgestern" in text_lower:
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")
    elif "gestern" in text_lower:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "heute" in text_lower:
        return today.strftime("%Y-%m-%d")

    # DD.MM.YYYY
    m = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
    if m:
        d, mon, y = m.groups()
        return f"{y}-{int(mon):02d}-{int(d):02d}"

    # DD.MM. (aktuelles Jahr)
    m = re.search(r'(\d{1,2})\.(\d{1,2})\.', text)
    if m:
        d, mon = m.groups()
        return f"{today.year}-{int(mon):02d}-{int(d):02d}"

    return today.strftime("%Y-%m-%d")


def parse_activity(text):
    """Parst eine Aktivität aus dem Text"""
    text_lower = text.lower()
    category = None
    value = None
    description = ""
    duration_min = None

    # Kategorie erkennen
    if "p90x" in text_lower:
        category = "P90X"
        value = "done"
    elif "fahrrad" in text_lower or "rad" in text_lower or "bike" in text_lower:
        category = "Fahrrad"
    elif "spazieren" in text_lower or "spaziergang" in text_lower or "wandern" in text_lower or "gehen" in text_lower:
        category = "Spazieren"

    if not category:
        print(f"❌ Kategorie nicht erkannt! Verfügbar: P90X, Spazieren, Fahrrad")
        return None

    # Optional: Dauer in Minuten für P90X (z.B. "P90X 45 min")
    m_duration = re.search(r'(\d+)\s*min', text_lower)
    if m_duration:
        duration_min = int(m_duration.group(1))

    # Wert parsen (km oder done)
    if category == "P90X":
        value = "done"
        # Beschreibung extrahieren (alles außer "P90X" und "done")
        desc = re.sub(r'(?i)p90x', '', text)
        desc = re.sub(r'(?i)done', '', desc)
        desc = re.sub(r'(?i)\d+\s*min', '', desc)
        desc = re.sub(r'(?i)gestern|vorgestern|heute|\d{1,2}\.\d{1,2}\.\d{0,4}', '', desc)
        description = desc.strip() or "P90X Training"
    else:
        # Suche nach km-Wert
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:km|kilometer)', text_lower)
        if m:
            value = m.group(1).replace(',', '.')
        else:
            # Versuche einfach eine Zahl zu finden
            m = re.search(r'(\d+(?:[.,]\d+)?)', text)
            if m:
                value = m.group(1).replace(',', '.')
            else:
                print(f"❌ Keine Kilometerangabe gefunden!")
                return None

        # Beschreibung extrahieren
        desc = re.sub(r'(?i)gestern|vorgestern|heute|\d{1,2}\.\d{1,2}\.\d{0,4}', '', text)
        desc = re.sub(r'\d+(?:[.,]\d+)?\s*(?:km|kilometer)?', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'(?i)fahrrad|rad|bike|spazieren|spaziergang|wandern|gehen', '', desc)
        desc = re.sub(r'(?i)\d+\s*min', '', desc)
        description = desc.strip() or category

    date = parse_date(text)

    return {
        "date": date,
        "category": category,
        "value": value,
        "description": description,
        "duration_min": duration_min,
    }


def add_activity(text):
    """Fügt eine Aktivität hinzu (mit Kalorienberechnung)"""
    activity = parse_activity(text)
    if not activity:
        return

    # Kalorien berechnen
    weight = _get_weight()
    calories, duration_min, speed = _calculate_calories(
        activity["category"],
        activity["value"],
        activity.get("duration_min"),
        weight
    )

    # activity.type ableiten
    activity_type = "strength" if activity["category"] == "P90X" else "cardio"

    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activities (date, category, value, description, type, duration_min, calories, speed_kmh, weight_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity["date"],
            activity["category"],
            activity["value"],
            activity["description"],
            activity_type,
            duration_min,
            calories,
            speed,
            weight,
        ))
        conn.commit()
        conn.close()

        emoji = {"P90X": "💪", "Spazieren": "🚶", "Fahrrad": "🚴"}
        e = emoji.get(activity["category"], "✅")

        print(f"{e} Aktivität gespeichert:")
        print(f"   📅 {activity['date']}")
        print(f"   📂 {activity['category']} ({activity_type})")
        if activity["category"] == "P90X":
            print(f"   ✅ {activity['value']} | {duration_min} min | {calories} kcal")
        else:
            print(f"   📏 {activity['value']} km | {duration_min} min | {calories} kcal")
            if speed:
                print(f"   🚀 Ø {speed} km/h")
        weight = _get_weight()
        print(f"   ⚖️  Gewicht: {weight} kg")
        print(f"   📝 {activity['description']}")
    except Exception as ex:
        print(f"❌ Fehler beim Speichern: {ex}")


# ─────────────────────────────────────────────────────────────
# Workout-Tracking (P90X done / missed / status)
# ─────────────────────────────────────────────────────────────

def _is_training_day(dt=None):
    """Prüft ob ein Tag ein Trainingstag ist (Mo=1, Mi=3, Fr=5)"""
    if dt is None:
        dt = datetime.now()
    return dt.weekday() in TRAINING_DAYS


def _get_workout_type_arg(args_text):
    """Extrahiert optionalen Workout-Typ (P90X, P90X2, P90X3) aus dem Argument"""
    if not args_text:
        return "P90X"
    text_upper = args_text.upper().strip()
    for t in ("P90X3", "P90X2", "P90X"):
        if t in text_upper:
            return t
    return "P90X"


def mark_done(workout_type="P90X", date_str=None):
    """Markiert einen Tag als erledigt (Workout + Activity)"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    is_training = _is_training_day(datetime.strptime(date_str, "%Y-%m-%d"))
    weight = _get_weight()
    calories, duration_min, _ = _calculate_calories("P90X", "done", P90X_DEFAULT_DURATION, weight)

    conn = _get_conn()
    cursor = conn.cursor()

    # workout_status eintragen/aktualisieren
    cursor.execute("""
        INSERT INTO workout_status (date, is_training_day, status, type, notes)
        VALUES (?, ?, 'done', ?, ?)
        ON CONFLICT(date) DO UPDATE SET status='done', type=excluded.type, notes=excluded.notes, created_at=CURRENT_TIMESTAMP
    """, (date_str, is_training, workout_type, f"{workout_type} Training absolviert"))

    # Auch in activities eintragen (für Konsistenz)
    cursor.execute("""
        INSERT INTO activities (date, category, value, description, type, duration_min, calories, weight_kg)
        VALUES (?, ?, 'done', ?, 'strength', ?, ?, ?)
        ON CONFLICT DO NOTHING
    """, (date_str, workout_type, f"{workout_type} Training", duration_min, calories, weight))

    conn.commit()
    conn.close()

    day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    print(f"💪 {workout_type} erledigt! ({date_str}, {day_name})")
    print(f"   ⏱️  Dauer: {duration_min} min | 🔥 {calories} kcal")


def mark_missed(date_str=None):
    """Markiert einen Tag als verpasst"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    is_training = _is_training_day(datetime.strptime(date_str, "%Y-%m-%d"))

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workout_status (date, is_training_day, status, type, notes)
        VALUES (?, ?, 'missed', 'P90X', ?)
        ON CONFLICT(date) DO UPDATE SET status='missed', notes=excluded.notes, created_at=CURRENT_TIMESTAMP
    """, (date_str, is_training, "Training verpasst"))
    conn.commit()
    conn.close()

    print(f"❌ Training verpasst: {date_str}")


def get_workout_status(days=14):
    """Zeigt Trainingstage der letzten N Tage"""
    today = datetime.now()
    conn = _get_conn()
    cursor = conn.cursor()

    lines = [f"📅 **Workout-Status (letzte {days} Tage)**\n"]
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        weekday = d.strftime("%a")
        is_training = _is_training_day(d)

        cursor.execute("SELECT status, type, notes FROM workout_status WHERE date = ?", (d_str,))
        row = cursor.fetchone()

        if row:
            status = row["status"] or "pending"
            wtype = row["type"] or "P90X"
        else:
            status = "rest" if not is_training else "pending"
            wtype = "P90X"

        icon = {
            "done": "✅",
            "missed": "❌",
            "rest": "🛌",
            "pending": "⏳",
        }.get(status, "⏳")

        training_mark = "💪" if is_training else "·"
        lines.append(f"  {icon} {d_str} ({weekday}) {training_mark} {wtype} – {status}")

    conn.close()
    return "\n".join(lines)


def get_workout_check():
    """JSON-Output für Workout-Check"""
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    is_training = _is_training_day(today)

    conn = _get_conn()
    cursor = conn.cursor()

    # Prüfe ob heute schon done
    cursor.execute("SELECT status FROM workout_status WHERE date = ?", (today_str,))
    row = cursor.fetchone()
    today_done = bool(row and row["status"] == "done")

    # Verpasste Tage in den letzten 14 Tagen
    missed_days = 0
    for i in range(14):
        d = today - timedelta(days=i)
        if not _is_training_day(d):
            continue
        d_str = d.strftime("%Y-%m-%d")
        cursor.execute("SELECT status FROM workout_status WHERE date = ?", (d_str,))
        r = cursor.fetchone()
        if r and r["status"] == "missed":
            missed_days += 1
        elif not r:
            # Wenn kein Eintrag und Trainingstag in der Vergangenheit → missed
            if d < today:
                missed_days += 1

    conn.close()

    # Sarkasmus-Trigger
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT sarcasm_threshold FROM workout_rules WHERE id = 1")
    row = cursor.fetchone()
    threshold = row["sarcasm_threshold"] if row else 2
    conn.close()

    sarcasm = missed_days >= threshold
    sarcasm_text = random.choice(SARCASM_LINES) if sarcasm else None

    result = {
        "training_day": is_training,
        "done": today_done,
        "missed_days": missed_days,
        "sarcasm_triggered": sarcasm,
        "sarcasm_text": sarcasm_text,
        "threshold": threshold,
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


def get_workout_stats():
    """Zeigt Workout-Statistiken (Streaks, verpasste Tage, Sarkasmus)"""
    conn = _get_conn()
    cursor = conn.cursor()

    # Alle workout_status Einträge
    cursor.execute("SELECT date, status FROM workout_status ORDER BY date")
    rows = cursor.fetchall()

    # Counts
    total_done = sum(1 for r in rows if r["status"] == "done")
    total_missed = sum(1 for r in rows if r["status"] == "missed")

    # Aktueller Streak (aufeinanderfolgende done-Tage)
    streak = 0
    # Prüfe vom heutigen Tag rückwärts
    today = datetime.now()
    for i in range(30):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        cursor.execute("SELECT status FROM workout_status WHERE date = ?", (d_str,))
        r = cursor.fetchone()
        if r and r["status"] == "done":
            streak += 1
        elif i == 0 and not r:
            # Heute noch kein Eintrag, ignorieren für Streak
            continue
        else:
            break

    # Verpasste Tage letzte 14 Tage
    missed_14 = 0
    for i in range(14):
        d = today - timedelta(days=i)
        if not _is_training_day(d):
            continue
        d_str = d.strftime("%Y-%m-%d")
        cursor.execute("SELECT status FROM workout_status WHERE date = ?", (d_str,))
        r = cursor.fetchone()
        if r and r["status"] == "missed":
            missed_14 += 1
        elif not r and d < today:
            missed_14 += 1

    cursor.execute("SELECT sarcasm_threshold FROM workout_rules WHERE id = 1")
    row = cursor.fetchone()
    threshold = row["sarcasm_threshold"] if row else 2
    conn.close()

    sarcasm = missed_14 >= threshold
    sarcasm_text = random.choice(SARCASM_LINES) if sarcasm else None

    lines = ["🏆 **Workout-Statistiken**\n"]
    lines.append(f"📊 Insgesamt erledigt: {total_done}")
    lines.append(f"📊 Insgesamt verpasst: {total_missed}")
    lines.append(f"🔥 Aktueller Streak: {streak} Tag(e)")
    lines.append(f"❌ Verpasst (letzte 14 Tage): {missed_14}")
    lines.append(f"🚨 Sarkasmus-Threshold: {threshold}")
    if sarcasm and sarcasm_text:
        lines.append(f"\n{sarcasm_text}")
    else:
        lines.append("\n🎩 Kein Sarkasmus nötig – die Lordschaft ist auf Kurs!")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Reports (Week/Month) – mit Kalorien
# ─────────────────────────────────────────────────────────────

def get_week_report():
    """Bericht für aktuelle Woche (Mo-So)"""
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6)
    end = end.replace(hour=23, minute=59, second=59)
    kw = today.isocalendar()[1]

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, value, calories, duration_min FROM activities
        WHERE date >= ? AND date <= ?
        ORDER BY date
    """, (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"📊 Keine Aktivitäten in KW {kw} ({start.strftime('%d.%m.')} - {end.strftime('%d.%m.')})."

    return _build_report(rows, f"🏃 WÖCHENTLICHER SPORT-BERICHT – KW {kw}", start, end)


def get_month_report(full=False):
    """Bericht für aktuellen Monat"""
    today = datetime.now()
    year, month = today.year, today.month
    start = datetime(year, month, 1)

    if full:
        last_day = __import__('calendar').monthrange(year, month)[1]
        end = datetime(year, month, last_day, 23, 59, 59)
        title = f"🏃 MONATS-BERICHT – {start.strftime('%B %Y')} (komplett)"
    else:
        end = today.replace(hour=23, minute=59, second=59)
        title = f"🏃 MONATS-BERICHT – {start.strftime('%B %Y')} (01.{month:02d}. bis heute)"

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, value, calories, duration_min FROM activities
        WHERE date >= ? AND date <= ?
        ORDER BY date
    """, (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"📊 Keine Aktivitäten in {start.strftime('%B %Y')}."

    return _build_report(rows, title, start, end)


def _build_report(rows, title, start, end):
    """Baut den Report-String auf"""
    stats = defaultdict(lambda: {"count": 0, "km": 0.0, "calories": 0, "duration": 0})
    total_calories = 0
    for cat, val, cal, dur in rows:
        stats[cat]["count"] += 1
        total_calories += cal or 0
        if dur:
            stats[cat]["duration"] += dur
        if cat != "P90X":
            try:
                stats[cat]["km"] += float(val)
            except (ValueError, TypeError):
                pass
        stats[cat]["calories"] += cal or 0

    lines = [f"**{title}**\n"]
    lines.append(f"Zeitraum: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}\n")

    # Pro Kategorie
    lines.append("📊 **Nach Kategorie:**")
    total_km = 0.0
    for cat in CATEGORIES:
        if cat in stats:
            count = stats[cat]["count"]
            cal = stats[cat]["calories"]
            dur = stats[cat]["duration"]
            if cat == "P90X":
                emoji = "💪"
                lines.append(f"  {emoji} {cat}: {count} Session(s) | {cal} kcal | {dur} min")
            else:
                emoji = "🚶" if cat == "Spazieren" else "🚴"
                km = stats[cat]["km"]
                total_km += km
                lines.append(f"  {emoji} {cat}: {km:.2f} km | {cal} kcal | {dur} min ({count}x)")

    # Gesamtübersicht
    total_sessions = sum(s["count"] for s in stats.values())
    total_duration = sum(s["duration"] for s in stats.values())
    lines.append(f"\n📈 **Gesamtübersicht:**")
    lines.append(f"   Sessions gesamt: {total_sessions}")
    if total_km > 0:
        lines.append(f"   Kilometer gesamt: {total_km:.2f} km")
    lines.append(f"   Kalorien gesamt: {total_calories} kcal")
    lines.append(f"   Dauer gesamt: {total_duration} min")

    # Emoji-Visualisierung
    lines.append(f"\n🎯 **Aktivitäts-Übersicht:**")
    for cat in CATEGORIES:
        if cat in stats:
            count = stats[cat]["count"]
            if cat == "P90X":
                bar = "💪" * min(count, 10)
                lines.append(f"   {cat}: {bar} ({count}x)")
            else:
                km = stats[cat]["km"]
                bar_len = min(int(km / 2) + 1, 15)
                bar = "█" * bar_len
                lines.append(f"   {cat}: {bar} {km:.1f} km")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Stats (Kalorien pro Aktivität)
# ─────────────────────────────────────────────────────────────

def get_stats():
    """Zeigt detaillierte Statistiken (inkl. Kalorien pro Aktivität)"""
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, COUNT(*) as cnt, SUM(calories) as total_cal,
               AVG(calories) as avg_cal, SUM(duration_min) as total_dur,
               AVG(speed_kmh) as avg_speed
        FROM activities
        GROUP BY category
    """)
    rows = cursor.fetchall()

    lines = ["📈 **Detaillierte Statistiken**\n"]

    for row in rows:
        cat = row["category"]
        cnt = row["cnt"]
        total_cal = row["total_cal"] or 0
        avg_cal = row["avg_cal"] or 0
        total_dur = row["total_dur"] or 0
        avg_speed = row["avg_speed"] or 0

        emoji = {"P90X": "💪", "Spazieren": "🚶", "Fahrrad": "🚴"}.get(cat, "✅")
        lines.append(f"{emoji} **{cat}**")
        lines.append(f"   Einträge: {cnt}")
        lines.append(f"   Kalorien gesamt: {int(total_cal)} kcal")
        lines.append(f"   Kalorien Ø: {int(avg_cal)} kcal/Session")
        lines.append(f"   Dauer gesamt: {total_dur} min")
        if avg_speed and cat != "P90X":
            lines.append(f"   Geschwindigkeit Ø: {avg_speed:.1f} km/h")
        lines.append("")

    # Gesamtkalorien
    cursor.execute("SELECT SUM(calories) as total FROM activities")
    total_row = cursor.fetchone()
    total = total_row["total"] or 0
    lines.append(f"🔥 **Gesamtkalorien aller Aktivitäten:** {int(total)} kcal")

    conn.close()
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# List (mit Kalorien)
# ─────────────────────────────────────────────────────────────

def list_activities(limit=10):
    """Zeigt die letzten Einträge (mit Kalorien)"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, category, value, description, calories, duration_min
        FROM activities
        ORDER BY date DESC, id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("📊 Keine Aktivitäten vorhanden.")
        return

    emoji = {"P90X": "💪", "Spazieren": "🚶", "Fahrrad": "🚴"}
    print(f"📋 **Letzte {len(rows)} Aktivitäten:**\n")
    for date, cat, val, desc, cal, dur in rows:
        e = emoji.get(cat, "✅")
        cal_str = f" | {cal} kcal" if cal else ""
        dur_str = f" | {dur} min" if dur else ""
        if cat in ("P90X", "P90X2", "P90X3") or val == "done":
            print(f"  {e} {date}: {cat} – {desc}{dur_str}{cal_str}")
        else:
            print(f"  {e} {date}: {cat} – {val} km – {desc}{dur_str}{cal_str}")


# ─────────────────────────────────────────────────────────────
# Seed
# ─────────────────────────────────────────────────────────────

def seed_data():
    """Trägt die vorab definierten Daten ein (mit Kalorien)"""
    seed = [
        ("2026-04-26", "Spazieren", "5.0", "Spazieren"),
        ("2026-04-25", "Spazieren", "4.24", "Spazieren"),
        ("2026-04-24", "Fahrrad", "17.7", "Fahrrad fahren"),
    ]
    weight = _get_weight()
    conn = _get_conn()
    cursor = conn.cursor()
    for date, cat, val, desc in seed:
        cal, dur, speed = _calculate_calories(cat, val, weight_kg=weight)
        cursor.execute("""
            INSERT INTO activities (date, category, value, description, type, duration_min, calories, speed_kmh, weight_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, cat, val, desc,
            "strength" if cat == "P90X" else "cardio",
            dur, cal, speed, weight,
        ))
    conn.commit()
    conn.close()
    print("✅ Seed-Daten eingetragen.")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sports Tracker v2.0")
    parser.add_argument("--init", action="store_true", help="Datenbank initialisieren/migrieren")
    parser.add_argument("--add", metavar="TEXT", help="Aktivität hinzufügen")
    parser.add_argument("--week", action="store_true", help="Wochenbericht (Mo-So)")
    parser.add_argument("--month", action="store_true", help="Monatsbericht (1. bis heute)")
    parser.add_argument("--month-full", action="store_true", help="Kompletter Monat")
    parser.add_argument("--list", action="store_true", help="Letzte 10 Einträge")
    parser.add_argument("--stats", action="store_true", help="Detaillierte Statistiken (Kalorien)")
    parser.add_argument("--weight", metavar="KG", type=float, help="Gewicht aktualisieren (kg)")

    # Workout-Tracking
    parser.add_argument("--done", metavar="TYPE", nargs="?", const="P90X",
                        help="Heute als erledigt markieren (default: P90X)")
    parser.add_argument("--missed", action="store_true", help="Heute als verpasst markieren")
    parser.add_argument("--workout-status", action="store_true", help="Trainingstage letzte 14 Tage")
    parser.add_argument("--workout-check", action="store_true", help="JSON: training_day, done, missed_days, sarcasm")
    parser.add_argument("--workout-stats", action="store_true", help="Streaks, verpasste Tage, Sarkasmus")

    args = parser.parse_args()

    # Datenbank-Initialisierung / Migration
    if args.init:
        init_db()
        return

    # Stelle sicher, dass DB existiert (mindestens migriert)
    if not DB_PATH.exists():
        print("❌ Datenbank nicht gefunden. Bitte zuerst --init ausführen.")
        sys.exit(1)
    _migrate_v1_to_v2()

    if args.add:
        add_activity(args.add)
    elif args.weight is not None:
        _set_weight(args.weight)
        print(f"⚖️  Gewicht aktualisiert: {args.weight} kg")
    elif args.week:
        print(get_week_report())
    elif args.month:
        print(get_month_report(full=False))
    elif args.month_full:
        print(get_month_report(full=True))
    elif args.stats:
        print(get_stats())
    elif args.list:
        list_activities()
    elif args.done is not None:
        mark_done(workout_type=args.done)
    elif args.missed:
        mark_missed()
    elif args.workout_status:
        print(get_workout_status())
    elif args.workout_check:
        print(get_workout_check())
    elif args.workout_stats:
        print(get_workout_stats())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
