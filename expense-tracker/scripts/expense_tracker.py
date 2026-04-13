#!/usr/bin/env python3
"""
Expense Tracker - Ausgaben-Tracking per Sprachnachricht
SQLite-basiert mit Reports nach Zeit, Kategorie und Händler
"""

import os
import sys
import re
import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Datenbank-Pfad
DB_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "expenses.db"

# Automatische Kategorie-Erkennung
CATEGORY_KEYWORDS = {
    "Lebensmittel": ["rewe", "lidl", "aldi", "edeka", "kaufland", "penny", "netto", "dm", "rossmann", "biomarkt", "bäckerei"],
    "Tanken": ["tankstelle", "aral", "shell", "avia", "agip", "bp", "esso", "jet", "omv", "total", "getankt", "tanken", "benzin", "diesel", "sprit"],
    "Transport": ["bahn", "db", "bus", "öpnv", "ticket", "fahrkarte", "parking", "parken"],
    "Freizeit": ["kino", "restaurant", "mc", "burger", "pizza", "bar", "club", "netflix", "spotify", "steam"],
    "Shopping": ["amazon", "ebay", "zalando", "h&m", "mediamarkt", "saturn", "ikea"],
    "Schule": ["schule", "bücher", "unterricht", "kurs", "lernen", "prüfung"],
    "Gesundheit": ["apotheke", "arzt", "krankenkasse", "versicherung", "sport"],
    "Sonstiges": []
}

def init_db():
    """Initialisiert die SQLite-Datenbank"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            store TEXT,
            description TEXT,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Datenbank initialisiert: {DB_PATH}")

def detect_category(text):
    """Erkennt Kategorie basierend auf Keywords"""
    text_lower = text.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return "Sonstiges"

def detect_store(text):
    """Erkennt den Händler/Supermarkt aus dem Text"""
    text_lower = text.lower()
    stores = ["rewe", "lidl", "aldi", "edeka", "kaufland", "penny", "netto", 
              "dm", "rossmann", "amazon", "ebay", "media markt", "saturn",
              "bäckerei", "apotheke", "arzt", "bahn", "db", "tankstelle"]
    
    for store in stores:
        if store in text_lower:
            return store.title()
    
    return None

def parse_expense(text):
    """Parst eine Ausgaben-Sprachnachricht"""
    # Betrag erkennen (z.B. "12,50€", "12.50", "12,50")
    amount_match = re.search(r'(\d+[,.]?\d*)\s*[€$]?', text)
    if not amount_match:
        return None
    
    amount_str = amount_match.group(1).replace(',', '.')
    amount = float(amount_str)
    
    # Kategorie erkennen
    category = detect_category(text)
    
    # Händler erkennen
    store = detect_store(text)
    
    # Beschreibung extrahieren (alles außer Betrag)
    description = re.sub(r'\d+[,.]?\d*\s*[€$]?', '', text).strip()
    description = re.sub(r'\s+', ' ', description)  # Mehrfache Leerzeichen entfernen
    
    return {
        "amount": amount,
        "category": category,
        "store": store,
        "description": description
    }

def add_expense(text):
    """Fügt eine Ausgabe hinzu"""
    data = parse_expense(text)
    
    if not data:
        print("❌ Konnte keinen Betrag erkennen!")
        print("💡 Beispiel: 'Habe 12,50€ bei Rewe für Milch ausgegeben'")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO expenses (amount, category, store, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (data["amount"], data["category"], data["store"], 
          data["description"], datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Ausgabe gespeichert:")
    print(f"   💰 {data['amount']:.2f}€")
    print(f"   📂 {data['category']}")
    if data['store']:
        print(f"   🏪 {data['store']}")
    if data['description']:
        print(f"   📝 {data['description']}")

def get_weekly_report():
    """Erstellt einen wöchentlichen Bericht"""
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE date >= ?
        GROUP BY category
        ORDER BY total DESC
    """, (week_ago,))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "📊 Keine Ausgaben diese Woche."
    
    total = sum(r[1] for r in results)
    
    report = [f"📊 **WÖCHENTLICHER AUSGABENBERICHT**\n"]
    report.append(f"Gesamt: **{total:.2f}€**\n")
    report.append("Nach Kategorie:")
    
    for category, amount in results:
        percentage = (amount / total) * 100
        report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
    
    return "\n".join(report)

def get_monthly_report():
    """Erstellt einen monatlichen Bericht"""
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Nach Kategorie
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE date >= ?
        GROUP BY category
        ORDER BY total DESC
    """, (month_ago,))
    
    category_results = cursor.fetchall()
    
    # Nach Händler
    cursor.execute("""
        SELECT store, SUM(amount) as total
        FROM expenses
        WHERE date >= ? AND store IS NOT NULL
        GROUP BY store
        ORDER BY total DESC
        LIMIT 5
    """, (month_ago,))
    
    store_results = cursor.fetchall()
    conn.close()
    
    if not category_results:
        return "📊 Keine Ausgaben diesen Monat."
    
    total = sum(r[1] for r in category_results)
    
    report = [f"📊 **MONATLICHER AUSGABENBERICHT**\n"]
    report.append(f"Gesamt: **{total:.2f}€**\n")
    
    report.append("Nach Kategorie:")
    for category, amount in category_results:
        percentage = (amount / total) * 100
        report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
    
    if store_results:
        report.append("\nTop Händler:")
        for store, amount in store_results:
            report.append(f"  • {store}: {amount:.2f}€")
    
    return "\n".join(report)

def get_store_comparison():
    """Vergleicht Ausgaben bei verschiedenen Händlern"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT store, SUM(amount) as total, COUNT(*) as visits
        FROM expenses
        WHERE store IS NOT NULL
        GROUP BY store
        ORDER BY total DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "📊 Keine Händler-Daten vorhanden."
    
    report = [f"🏪 **HÄNDLER-VERGLEICH**\n"]
    
    for store, total, visits in results:
        avg_per_visit = total / visits if visits > 0 else 0
        report.append(f"  • {store}: {total:.2f}€ ({visits}x, Ø {avg_per_visit:.2f}€)")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Expense Tracker - Ausgaben verfolgen")
    parser.add_argument("text", nargs="?", help="Ausgabe als Text (z.B. '12,50€ bei Rewe')")
    parser.add_argument("--init", action="store_true", help="Datenbank initialisieren")
    parser.add_argument("--weekly", action="store_true", help="Wöchentlicher Bericht")
    parser.add_argument("--monthly", action="store_true", help="Monatlicher Bericht")
    parser.add_argument("--stores", action="store_true", help="Händler-Vergleich")
    parser.add_argument("--list", action="store_true", help="Letzte 10 Einträge anzeigen")
    
    args = parser.parse_args()
    
    if args.init:
        init_db()
    elif args.weekly:
        print(get_weekly_report())
    elif args.monthly:
        print(get_monthly_report())
    elif args.stores:
        print(get_store_comparison())
    elif args.list:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT date, amount, category, store FROM expenses ORDER BY date DESC LIMIT 10")
        results = cursor.fetchall()
        conn.close()
        
        print("📋 **Letzte 10 Ausgaben:**")
        for date, amount, category, store in results:
            store_str = f" ({store})" if store else ""
            print(f"  {date[:10]}: {amount:.2f}€ - {category}{store_str}")
    elif args.text:
        add_expense(args.text)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
