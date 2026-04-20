#!/usr/bin/env python3
"""
Speichert AP1-Training Antworten in die Datenbank
Nutzen: python3 save_learning_answer.py <question_id> <answer> <correct:0/1>
"""

import sys
import sqlite3
from datetime import date, datetime
from pathlib import Path

DB_PATH = '/home/node/.openclaw/workspace/data/james.db'

def save_answer(question_id, user_answer, is_correct, category=""):
    """Speichert einen Lernversuch"""
    today = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Versuch speichern
        cursor.execute('''
            INSERT INTO learning_attempts 
            (question_id, user_answer, correct, timestamp, session_date)
            VALUES (?, ?, ?, datetime('now'), ?)
        ''', (question_id, user_answer, 1 if is_correct else 0, today))
        
        # Frage-Statistik aktualisieren
        cursor.execute('''
            UPDATE learning_questions 
            SET total_attempts = total_attempts + 1,
                correct_attempts = correct_attempts + ?,
                last_shown = datetime('now')
            WHERE id = ?
        ''', (1 if is_correct else 0, question_id))
        
        conn.commit()
        print(f"✅ Gespeichert: {question_id} = {user_answer} ({'richtig' if is_correct else 'falsch'})")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
    finally:
        conn.close()

def update_session_stats(topics_list):
    """Aktualisiert die Session-Statistik für heute"""
    today = date.today().isoformat()
    topics_str = ','.join(topics_list)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Heutige Versuche zählen
    cursor.execute('''
        SELECT COUNT(*), SUM(correct)
        FROM learning_attempts
        WHERE date(timestamp) = date('now')
    ''')
    total, correct = cursor.fetchone()
    total = total or 0
    correct = correct or 0
    wrong = total - correct
    percentage = round((correct / total) * 100) if total > 0 else 0
    
    # Session aktualisieren
    cursor.execute('''
        INSERT INTO learning_sessions 
        (session_date, questions_count, correct_count, wrong_count, percentage, topics)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_date) DO UPDATE SET
            questions_count = ?,
            correct_count = ?,
            wrong_count = ?,
            percentage = ?,
            topics = ?
    ''', (today, total, correct, wrong, percentage, topics_str,
          total, correct, wrong, percentage, topics_str))
    
    conn.commit()
    conn.close()
    
    print(f"📊 Session aktualisiert: {correct}/{total} ({percentage}%)")

def get_weekly_stats():
    """Holt Wochenstatistik"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Diese Woche (seit Sonntag)
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts 
        WHERE timestamp >= date('now', 'weekday 0', '-7 days')
    ''')
    
    total, correct = cursor.fetchone()
    total = total or 0
    correct = correct or 0
    
    # Tages-Statistik
    cursor.execute('''
        SELECT 
            date(timestamp) as day,
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts 
        WHERE timestamp >= date('now', 'weekday 0', '-7 days')
        GROUP BY date(timestamp)
        ORDER BY day ASC
    ''')
    
    days = cursor.fetchall()
    
    # Themen-Statistik
    cursor.execute('''
        SELECT 
            lq.category,
            COUNT(*) as attempts,
            SUM(CASE WHEN la.correct = 1 THEN 1 ELSE 0 END) as correct
        FROM learning_attempts la
        JOIN learning_questions lq ON la.question_id = lq.id
        WHERE la.timestamp >= date('now', 'weekday 0', '-7 days')
        GROUP BY lq.category
    ''')
    
    topics = cursor.fetchall()
    conn.close()
    
    return {
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'percentage': round(100 * correct / total, 1) if total > 0 else 0,
        'days': days,
        'topics': topics
    }

def show_stats():
    """Zeigt aktuelle Statistik"""
    stats = get_weekly_stats()
    
    print("\n" + "="*50)
    print("📊 AP1-TRAINING STATISTIK")
    print("="*50)
    
    print(f"\n🗓️  Diese Woche:")
    print(f"   Gesamt: {stats['total']} Fragen")
    print(f"   ✅ Richtig: {stats['correct']}")
    print(f"   ❌ Falsch: {stats['wrong']}")
    print(f"   📈 Quote: {stats['percentage']}%")
    
    if stats['days']:
        print(f"\n📅 Täglich:")
        for day in stats['days']:
            pct = round(100 * day[2] / day[1], 0) if day[1] > 0 else 0
            emoji = '🟢' if pct >= 67 else '🟡' if pct >= 50 else '🔴'
            print(f"   {emoji} {day[0]}: {day[2]}/{day[1]} ({int(pct)}%)")
    
    if stats['topics']:
        print(f"\n📚 Nach Themen:")
        for topic in stats['topics']:
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            print(f"   {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
    
    print("="*50)

def get_monthly_stats(year=None, month=None):
    """Holt Monatsstatistik"""
    from datetime import datetime
    
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Monats-Filter
    month_str = f"{year}-{month:02d}"
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts 
        WHERE strftime('%Y-%m', timestamp) = ?
    ''', (month_str,))
    
    total, correct = cursor.fetchone()
    total = total or 0
    correct = correct or 0
    
    # Tages-Statistik
    cursor.execute('''
        SELECT 
            date(timestamp) as day,
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts 
        WHERE strftime('%Y-%m', timestamp) = ?
        GROUP BY date(timestamp)
        ORDER BY day ASC
    ''', (month_str,))
    
    days = cursor.fetchall()
    
    # Themen-Statistik
    cursor.execute('''
        SELECT 
            lq.category,
            COUNT(*) as attempts,
            SUM(CASE WHEN la.correct = 1 THEN 1 ELSE 0 END) as correct
        FROM learning_attempts la
        JOIN learning_questions lq ON la.question_id = lq.id
        WHERE strftime('%Y-%m', la.timestamp) = ?
        GROUP BY lq.category
    ''', (month_str,))
    
    topics = cursor.fetchall()
    conn.close()
    
    return {
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'percentage': round(100 * correct / total, 1) if total > 0 else 0,
        'days': days,
        'topics': topics,
        'month': month_str
    }

def get_all_time_stats():
    """Holt Gesamtstatistik"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts
    ''')
    
    total, correct = cursor.fetchone()
    total = total or 0
    correct = correct or 0
    
    # Themen-Statistik
    cursor.execute('''
        SELECT 
            lq.category,
            COUNT(*) as attempts,
            SUM(CASE WHEN la.correct = 1 THEN 1 ELSE 0 END) as correct
        FROM learning_attempts la
        JOIN learning_questions lq ON la.question_id = lq.id
        GROUP BY lq.category
    ''')
    
    topics = cursor.fetchall()
    
    # Lern-Tage
    cursor.execute('''
        SELECT COUNT(DISTINCT date(timestamp)) FROM learning_attempts
    ''')
    learning_days = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'percentage': round(100 * correct / total, 1) if total > 0 else 0,
        'topics': topics,
        'learning_days': learning_days
    }

def show_monthly_stats(year=None, month=None):
    """Zeigt Monatsstatistik"""
    stats = get_monthly_stats(year, month)
    
    print("\n" + "="*50)
    print(f"📅 MONATSSTATISTIK - {stats['month']}")
    print("="*50)
    
    print(f"\n📊 Ergebnis:")
    print(f"   Gesamt: {stats['total']} Fragen")
    print(f"   ✅ Richtig: {stats['correct']}")
    print(f"   ❌ Falsch: {stats['wrong']}")
    print(f"   📈 Quote: {stats['percentage']}%")
    
    if stats['days']:
        print(f"\n📆 Tage gelernt: {len(stats['days'])}")
    
    if stats['topics']:
        print(f"\n📚 Nach Themen:")
        # Nach Quote sortieren
        sorted_topics = sorted(stats['topics'], 
                              key=lambda x: (x[2]/x[1] if x[1] > 0 else 0), 
                              reverse=True)
        for topic in sorted_topics:
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            print(f"   {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
    
    print("="*50)

def show_all_time_stats():
    """Zeigt Gesamtstatistik"""
    stats = get_all_time_stats()
    
    print("\n" + "="*50)
    print("🏆 GESAMTSTATISTIK - AP1 Training")
    print("="*50)
    
    print(f"\n📊 Ergebnis:")
    print(f"   Lern-Tage: {stats['learning_days']}")
    print(f"   Gesamt: {stats['total']} Fragen")
    print(f"   ✅ Richtig: {stats['correct']}")
    print(f"   ❌ Falsch: {stats['wrong']}")
    print(f"   📈 Erfolgsquote: {stats['percentage']}%")
    
    if stats['topics']:
        print(f"\n📚 Themen-Ranking:")
        # Nach Quote sortieren
        sorted_topics = sorted(stats['topics'], 
                              key=lambda x: (x[2]/x[1] if x[1] > 0 else 0), 
                              reverse=True)
        for i, topic in enumerate(sorted_topics, 1):
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {medal} {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
    
    print("="*50)

def generate_weekly_report():
    """Generiert Wochenbericht für Freitag"""
    stats = get_weekly_stats()
    
    report = []
    report.append("📊 **WOCHENBERICHT - AP1 Training**")
    report.append(f"🗓️ Woche vom {datetime.now().strftime('%d.%m.%Y')}")
    report.append("")
    report.append(f"📈 **Gesamt:** {stats['correct']}/{stats['total']} ({stats['percentage']}%)")
    report.append(f"   ✅ Richtig: {stats['correct']}")
    report.append(f"   ❌ Falsch: {stats['wrong']}")
    report.append("")
    
    if stats['topics']:
        report.append("📚 **Themenergebnisse:**")
        # Nach Quote sortieren
        sorted_topics = sorted(stats['topics'], 
                              key=lambda x: (x[2]/x[1] if x[1] > 0 else 0), 
                              reverse=True)
        for topic in sorted_topics:
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            emoji = '🟢' if pct >= 80 else '🟡' if pct >= 60 else '🔴'
            report.append(f"   {emoji} {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
        
        # Schwächstes Thema
        if len(sorted_topics) > 0:
            weakest = sorted_topics[-1]
            weakest_pct = round(100 * weakest[2] / weakest[1], 0) if weakest[1] > 0 else 0
            if weakest_pct < 70:
                report.append("")
                report.append(f"💡 **Empfehlung:** Mehr üben: {weakest[0]} (nur {weakest_pct}%)")
    
    return "\n".join(report)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 ap1_tracker.py stats [--week|--month|--all]")
        print("  python3 ap1_tracker.py report [--week]")
        print("  python3 ap1_tracker.py save <question_id> <answer> <0|1> [category]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'stats':
        if len(sys.argv) > 2 and sys.argv[2] == '--month':
            show_monthly_stats()
        elif len(sys.argv) > 2 and sys.argv[2] == '--all':
            show_all_time_stats()
        else:
            show_stats()  # Default: weekly
    
    elif cmd == 'report':
        if len(sys.argv) > 2 and sys.argv[2] == '--week':
            print(generate_weekly_report())
        else:
            print(generate_weekly_report())
    
    elif cmd == 'save':
        if len(sys.argv) < 6:
            print("❌ Fehler: Benötige question_id, answer, correct (0/1), category")
            print("   Beispiel: python3 ap1_tracker.py save sec-003 B 1 'IT-Sicherheit'")
            sys.exit(1)
        
        question_id = sys.argv[2]
        answer = sys.argv[3]
        correct = int(sys.argv[4])
        category = sys.argv[5]
        
        save_answer(question_id, answer, correct, category)
    
    else:
        print(f"❌ Unbekannter Befehl: {cmd}")
        print("Verfügbare Befehle: stats, report, save")
        sys.exit(1)
