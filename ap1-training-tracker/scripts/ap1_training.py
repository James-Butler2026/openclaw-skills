#!/usr/bin/env python3
"""
AP1 Training - IHK Fachinformatiker Lern-Tracker
Optimierte Version mit Shared Database Module
==============================================
Usage:
    python3 ap1_training.py --daily         # 3 zufällige Fragen
    python3 ap1_training.py --save <id> <ans> <correct> <cat>  # Antwort speichern
    python3 ap1_training.py --stats         # Statistiken
"""

import sys
import json
import argparse
from datetime import datetime, date

from shared_db import (
    init_main_db,
    get_random_questions_efficient,
    save_attempt,
    get_weekly_stats,
    get_monthly_stats,
    get_all_time_stats,
    invalidate_stats_cache,
    invalidate_question_cache,
    DB_MAIN,
    DB_QUESTIONS
)

TOPIC_ID = "-1003765464477:13"

THEMEN = [
    'IT-Grundlagen', 'Software-Entwicklung', 'Datenbanken',
    'IT-Sicherheit', 'Projektmanagement', 'Wirtschaft'
]


def format_daily_questions(questions):
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
    parser.add_argument('--refresh', action='store_true', help='Cache leeren und neu laden')
    args = parser.parse_args()
    
    init_main_db()
    
    if args.refresh:
        invalidate_stats_cache()
        invalidate_question_cache()
        print("✅ Cache geleert")
        return
    
    if args.daily:
        questions = get_random_questions_efficient(3)
        print(format_daily_questions(questions))
        print("\n---JSON---")
        print(json.dumps({'questions': questions}, ensure_ascii=False))
    
    elif args.save:
        qid, ans, corr, cat = args.save
        save_attempt(qid, ans, corr == '1', cat)
        print(f"✅ Gespeichert: {qid}")
    
    elif args.stats:
        s = get_weekly_stats()
        print(f"📊 Wochenstatistik:")
        print(f"   Gesamt: {s['total']}")
        print(f"   ✅ Richtig: {s['correct']}")
        print(f"   ❌ Falsch: {s['wrong']}")
        print(f"   📈 Quote: {s['percentage']}%")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
