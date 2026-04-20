#!/usr/bin/env python3
"""
AP1 Tracker - Statistiken und Speichern
Optimierte Version mit Shared Database Module
=========================================
Usage:
    python3 ap1_tracker.py stats [--week|--month|--all]
    python3 ap1_tracker.py save <question_id> <answer> <0|1> [category]
    python3 ap1_tracker.py report [--week]
"""

import sys
import sqlite3
import argparse
from datetime import datetime, date
from pathlib import Path

from shared_db import (
    get_main_db,
    get_weekly_stats,
    get_monthly_stats,
    get_all_time_stats,
    save_attempt,
    init_main_db,
    invalidate_stats_cache
)

DB_PATH = '/home/node/.openclaw/workspace/data/james.db'


def save_answer(question_id, user_answer, is_correct, category=""):
    save_attempt(question_id, user_answer, is_correct, category)
    print(f"✅ Gespeichert: {question_id} = {user_answer} ({'richtig' if is_correct else 'falsch'})")


def show_stats():
    stats = get_weekly_stats()
    
    print("\n" + "="*50)
    print("📊 AP1-TRAINING STATISTIK")
    print("="*50)
    
    print(f"\n🗓️  Diese Woche:")
    print(f"   Gesamt: {stats['total']} Fragen")
    print(f"   ✅ Richtig: {stats['correct']}")
    print(f"   ❌ Falsch: {stats['wrong']}")
    print(f"   📈 Quote: {stats['percentage']}%")
    
    if stats.get('days'):
        print(f"\n📅 Täglich:")
        for day in stats['days']:
            pct = round(100 * day[2] / day[1], 0) if day[1] > 0 else 0
            emoji = '🟢' if pct >= 67 else '🟡' if pct >= 50 else '🔴'
            print(f"   {emoji} {day[0]}: {day[2]}/{day[1]} ({int(pct)}%)")
    
    if stats.get('topics'):
        print(f"\n📚 Nach Themen:")
        for topic in stats['topics']:
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            print(f"   {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
    
    print("="*50)


def show_monthly_stats(year=None, month=None):
    stats = get_monthly_stats(year, month)
    
    print("\n" + "="*50)
    print(f"📅 MONATSSTATISTIK - {stats['month']}")
    print("="*50)
    
    print(f"\n📊 Ergebnis:")
    print(f"   Gesamt: {stats['total']} Fragen")
    print(f"   ✅ Richtig: {stats['correct']}")
    print(f"   ❌ Falsch: {stats['wrong']}")
    print(f"   📈 Quote: {stats['percentage']}%")
    
    if stats.get('days'):
        print(f"\n📆 Tage gelernt: {len(stats['days'])}")
    
    if stats.get('topics'):
        print(f"\n📚 Nach Themen:")
        sorted_topics = sorted(stats['topics'], 
                              key=lambda x: (x[2]/x[1] if x[1] > 0 else 0), 
                              reverse=True)
        for topic in sorted_topics:
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            print(f"   {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
    
    print("="*50)


def show_all_time_stats():
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
    
    if stats.get('topics'):
        print(f"\n📚 Themen-Ranking:")
        sorted_topics = sorted(stats['topics'], 
                              key=lambda x: (x[2]/x[1] if x[1] > 0 else 0), 
                              reverse=True)
        for i, topic in enumerate(sorted_topics, 1):
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {medal} {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
    
    print("="*50)


def generate_weekly_report():
    stats = get_weekly_stats()
    
    report = []
    report.append("📊 **WOCHENBERICHT - AP1 Training**")
    report.append(f"🗓️ Woche vom {datetime.now().strftime('%d.%m.%Y')}")
    report.append("")
    report.append(f"📈 **Gesamt:** {stats['correct']}/{stats['total']} ({stats['percentage']}%)")
    report.append(f"   ✅ Richtig: {stats['correct']}")
    report.append(f"   ❌ Falsch: {stats['wrong']}")
    report.append("")
    
    if stats.get('topics'):
        report.append("📚 **Themenergebnisse:**")
        sorted_topics = sorted(stats['topics'], 
                              key=lambda x: (x[2]/x[1] if x[1] > 0 else 0), 
                              reverse=True)
        for topic in sorted_topics:
            pct = round(100 * topic[2] / topic[1], 0) if topic[1] > 0 else 0
            emoji = '🟢' if pct >= 80 else '🟡' if pct >= 60 else '🔴'
            report.append(f"   {emoji} {topic[0]}: {topic[2]}/{topic[1]} ({int(pct)}%)")
        
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
            show_stats()
    
    elif cmd == 'report':
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
