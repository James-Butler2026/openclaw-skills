#!/usr/bin/env python3
"""
AP1 Training - IHK Fachinformatiker Lern-Tracker
SQLite-Version mit externer Datenbank
======================================
Usage:
    python3 ap1_training.py --daily         # 3 zufällige Fragen
    python3 ap1_training.py --save <id> <ans> <correct> <cat>  # Antwort speichern
    python3 ap1_training.py --stats         # Statistiken
"""

import sys
import json
import random
import sqlite3
import argparse
from datetime import datetime, date
from pathlib import Path

# Pfade
DB_MAIN = '/home/node/.openclaw/workspace/data/james.db'
DB_QUESTIONS = '/home/node/.openclaw/workspace/skills/ap1-training-tracker/data/questions.db'
TOPIC_ID = "-1003765464477:13"

THEMEN = [
    'IT-Grundlagen', 'Software-Entwicklung', 'Datenbanken',
    'IT-Sicherheit', 'Projektmanagement', 'Wirtschaft'
]

def init_main_db():
    """Hauptdatenbank für Versuche und Statistik"""
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS learning_attempts (
        id INTEGER PRIMARY KEY,
        question_id TEXT,
        user_answer TEXT,
        correct INTEGER,
        timestamp TIMESTAMP,
        session_date DATE
    )''')
    conn.commit()
    conn.close()

def get_random_questions(count=3):
    """Zufällige Fragen aus SQLite-DB holen"""
    conn = sqlite3.connect(DB_QUESTIONS)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Zufällige Fragen aus verschiedenen Kategorien
    cursor.execute('''SELECT * FROM questions 
                      ORDER BY RANDOM() 
                      LIMIT ?''', (count,))
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    for row in rows:
        questions.append({
            'id': row['id'],
            'question': row['question'],
            'options': json.loads(row['options']),
            'correct': row['correct'],
            'explanation': row['explanation'],
            'category': row['category'],
            'difficulty': row['difficulty']
        })
    return questions

def save_attempt(question_id, user_answer, is_correct, category):
    """Versuch speichern"""
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO learning_attempts 
                      VALUES (NULL,?,?,?,datetime("now"),?)''',
        (question_id, user_answer, 1 if is_correct else 0, today))
    conn.commit()
    conn.close()

def get_stats():
    """Statistiken abrufen"""
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*), SUM(correct) FROM learning_attempts 
                      WHERE timestamp >= date("now", "-7 days")''')
    total, correct = cursor.fetchone()
    
    cursor.execute('''SELECT COUNT(*) FROM learning_attempts 
                      WHERE timestamp >= date("now", "-7 days") 
                      AND correct = 0''')
    wrong = cursor.fetchone()[0]
    conn.close()
    
    return {
        'total': total or 0,
        'correct': correct or 0,
        'wrong': wrong or 0,
        'percentage': round((correct/total)*100, 1) if total else 0
    }

def format_daily_questions(questions):
    """Fragen formatieren wie im Cron"""
    output = []
    output.append("=" * 50)
    output.append("📚 TÄGLICHE AP1-ÜBUNG")
    output.append("=" * 50)
    output.append("")
    
    for i, q in enumerate(questions, 1):
        output.append(f"📱 {q['category']}")
        output.append(f"\n{i}. {q['question']}")
        for opt in q['options']:
            output.append(f"   {opt}")
        output.append("")
    
    output.append("Antwortet mit A, B, C oder D!")
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--daily', action='store_true', help='3 zufällige Fragen')
    parser.add_argument('--save', nargs=4, help='Antwort speichern: ID ANSWER CORRECT CATEGORY')
    parser.add_argument('--stats', action='store_true', help='Statistiken anzeigen')
    args = parser.parse_args()
    
    init_main_db()
    
    if args.daily:
        questions = get_random_questions(3)
        print(format_daily_questions(questions))
        # Auch als JSON für Cron
        print("\n---JSON---")
        print(json.dumps({'questions': questions}, ensure_ascii=False))
    
    elif args.save:
        qid, ans, corr, cat = args.save
        save_attempt(qid, ans, corr == '1', cat)
        print(f"✅ Gespeichert: {qid}")
    
    elif args.stats:
        s = get_stats()
        print(f"📊 Wochenstatistik:")
        print(f"   Gesamt: {s['total']}")
        print(f"   ✅ Richtig: {s['correct']}")
        print(f"   ❌ Falsch: {s['wrong']}")
        print(f"   📈 Quote: {s['percentage']}%")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
