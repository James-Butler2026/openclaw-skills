#!/usr/bin/env python3
"""
AP1 Training - IHK Fachinformatiker Lern-Tracker
Interaktive Version - Fragen einzeln nacheinander
==============================================
Usage:
    python3 ap1_training.py --start              # Quiz starten (Frage 1)
    python3 ap1_training.py --answer A           # Antwort auf aktuelle Frage
    python3 ap1_training.py --status             # Aktueller Quiz-Status
    python3 ap1_training.py --cancel             # Quiz abbrechen
    python3 ap1_training.py --stats               # Statistiken
    python3 ap1_training.py --daily              # 3 Fragen auf einmal (alt)
    python3 ap1_training.py --save <id> <ans> <correct> <cat>  # Manuell speichern
"""

import sys
import json
import argparse
from datetime import datetime, date
from pathlib import Path

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
STATE_FILE = Path("/tmp/ap1_session_state.json")

THEMEN = [
    'IT-Grundlagen', 'Software-Entwicklung', 'Datenbanken',
    'IT-Sicherheit', 'Projektmanagement', 'Wirtschaft'
]


# ── State Management ─────────────────────────────────

def load_state():
    """Lädt den aktuellen Quiz-Status"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None

def save_state(state):
    """Speichert den Quiz-Status"""
    STATE_FILE.write_text(json.dumps(state, indent=2))

def clear_state():
    """Löscht den Quiz-Status"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


# ── Formatting ────────────────────────────────────────

def format_question(q, num, total):
    """Formatiert eine einzelne Frage für Telegram"""
    lines = []
    lines.append(f"📚 **Frage {num}/{total}** | *{q['category']}*")
    lines.append("")
    lines.append(f"❓ {q['question']}")
    lines.append("")
    for opt in q['options']:
        lines.append(f"   {opt}")
    lines.append("")
    lines.append("_Antworte mit A, B, C oder D_")
    return "\n".join(lines)

def format_feedback(q, user_answer, is_correct):
    """Formatiert Feedback nach Antwort"""
    correct_opt = q['correct']
    correct_text = next((opt for opt in q['options'] if opt.startswith(correct_opt + ")")), "")
    
    if is_correct:
        lines = ["✅ **Richtig!**"]
    else:
        lines = ["❌ **Falsch!**"]
        lines.append(f"Deine Antwort: {user_answer}")
    
    lines.append(f"Richtig: {correct_text}")
    
    if q.get('explanation'):
        lines.append("")
        lines.append(f"💡 {q['explanation']}")
    
    return "\n".join(lines)

def format_result(state):
    """Formatiert das Endergebnis"""
    results = state['results']
    correct_count = sum(1 for r in results if r['correct'])
    total = len(results)
    
    lines = []
    lines.append("─" * 30)
    lines.append("")
    lines.append("🏁 **Quiz beendet!**")
    lines.append("")
    lines.append(f"📊 Ergebnis: {correct_count}/{total} richtig")
    lines.append(f"📈 Quote: {int(correct_count/total*100)}%")
    lines.append("")
    
    # Nach Themen
    topics = {}
    for r in results:
        t = r['category']
        if t not in topics:
            topics[t] = {"correct": 0, "total": 0}
        topics[t]["total"] += 1
        if r['correct']:
            topics[t]["correct"] += 1
    
    if topics:
        lines.append("📚 Nach Themen:")
        for t, stats in topics.items():
            emoji = "✅" if stats["correct"] == stats["total"] else "⚠️"
            lines.append(f"{emoji} {t}: {stats['correct']}/{stats['total']}")
        lines.append("")
    
    lines.append("_Schreibe **quiz** für eine neue Runde!_")
    
    return "\n".join(lines)


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


# ── Interactive Commands ─────────────────────────────

def cmd_start():
    """Startet ein neues Quiz"""
    # Alte Session löschen falls vorhanden
    clear_state()
    
    # 3 zufällige Fragen holen
    questions = get_random_questions_efficient(3)
    
    if not questions:
        return "❌ Fehler: Keine Fragen gefunden!"
    
    # State speichern
    state = {
        "status": "active",
        "current_q": 0,
        "questions": questions,
        "results": []
    }
    save_state(state)
    
    # Frage 1 ausgeben
    return format_question(questions[0], 1, len(questions))

def cmd_answer(user_answer):
    """Verarbeitet eine Antwort"""
    state = load_state()
    
    if not state or state.get("status") != "active":
        return "❌ Kein aktives Quiz! Schreibe **quiz** um zu starten."
    
    user_answer = user_answer.upper()
    if user_answer not in ["A", "B", "C", "D"]:
        return "❓ Ungültige Eingabe! Bitte antworte mit **A**, **B**, **C** oder **D**."
    
    q_idx = state["current_q"]
    questions = state["questions"]
    current_q = questions[q_idx]
    
    # Prüfen ob richtig
    is_correct = user_answer == current_q["correct"]
    
    # Speichern in DB
    save_attempt(current_q["id"], user_answer, is_correct, current_q["category"])
    
    # Ergebnis merken
    state["results"].append({
        "question_id": current_q["id"],
        "category": current_q["category"],
        "correct": is_correct
    })
    
    # Feedback
    feedback = format_feedback(current_q, user_answer, is_correct)
    
    # Nächste Frage oder Ende?
    if q_idx + 1 >= len(questions):
        # Alle beantwortet
        result = format_result(state)
        clear_state()
        return feedback + "\n\n" + result
    else:
        # Nächste Frage
        state["current_q"] = q_idx + 1
        save_state(state)
        
        next_q = questions[q_idx + 1]
        next_text = "─" * 30 + "\n\n" + format_question(next_q, q_idx + 2, len(questions))
        return feedback + "\n\n" + next_text

def cmd_status():
    """Zeigt aktuellen Status"""
    state = load_state()
    
    if not state or state.get("status") != "active":
        return "❌ Kein aktives Quiz. Schreibe **quiz** um zu starten."
    
    q_idx = state["current_q"]
    questions = state["questions"]
    current_q = questions[q_idx]
    
    return format_question(current_q, q_idx + 1, len(questions))

def cmd_cancel():
    """Bricht Quiz ab"""
    clear_state()
    return "🗑️ Quiz abgebrochen. Schreibe **quiz** für eine neue Runde!"


# ── Main ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', action='store_true', help='Quiz starten (interaktiv)')
    parser.add_argument('--answer', help='Antwort auf aktuelle Frage (A/B/C/D)')
    parser.add_argument('--status', action='store_true', help='Aktuellen Status anzeigen')
    parser.add_argument('--cancel', action='store_true', help='Quiz abbrechen')
    parser.add_argument('--daily', action='store_true', help='3 zufällige Fragen (alt)')
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
    
    if args.start:
        print(cmd_start())
    
    elif args.answer:
        print(cmd_answer(args.answer))
    
    elif args.status:
        print(cmd_status())
    
    elif args.cancel:
        print(cmd_cancel())
    
    elif args.daily:
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

