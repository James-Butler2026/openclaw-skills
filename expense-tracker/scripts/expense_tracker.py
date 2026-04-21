#!/usr/bin/env python3
"""
Expense Tracker v2.1 - Überarbeitet
Ausgaben-Tracking per Sprachnachricht
SQLite-basiert mit Reports, JSON-Konfiguration, Backup & CSV Export
"""

import os
import sys
import re
import sqlite3
import argparse
import json
import shutil
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pfade
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DB_PATH = WORKSPACE / "data" / "expenses.db"
CONFIG_DIR = WORKSPACE / "skills" / "expense-tracker" / "config"
CONFIG_FILE = CONFIG_DIR / "categories.json"

# Standard-Kategorien
DEFAULT_CATEGORIES = {
    "Lebensmittel": ["rewe", "lidl", "aldi", "edeka", "kaufland", "penny", "netto", "dm", "rossmann", "biomarkt", "bäckerei"],
    "Tanken": ["tankstelle", "aral", "shell", "avia", "agip", "bp", "esso", "jet", "omv", "total", "getankt", "tanken", "benzin", "diesel", "sprit"],
    "Transport": ["bahn", "db", "bus", "öpnv", "ticket", "fahrkarte", "parking", "parken"],
    "Freizeit": ["kino", "restaurant", "mc", "burger", "pizza", "bar", "club", "netflix", "spotify", "steam"],
    "Shopping": ["amazon", "ebay", "zalando", "h&m", "mediamarkt", "saturn", "ikea"],
    "Schule": ["schule", "bücher", "unterricht", "kurs", "lernen", "prüfung"],
    "Gesundheit": ["apotheke", "arzt", "krankenkasse", "versicherung", "sport"],
    "Anlagevermögen": ["crypto", "krypto", "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "ripple", "xrp", "börse", "invest", "aktie", "fond"],
    "Essen auswärts": ["essen", "auswärts", "restaurant", "mcdonalds", "burger king", "kfc", "subway", "pizzeria", "imbiss", "döner", "sushi", "chinesisch", "italienisch"],
    "Sonstiges": []
}


def load_categories():
    """Lädt Kategorien aus JSON oder erstellt Default"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Konnte Kategorien nicht laden: {e}, nutze Defaults")
    
    # Erstelle Default-Config
    save_categories(DEFAULT_CATEGORIES)
    return DEFAULT_CATEGORIES


def save_categories(categories):
    """Speichert Kategorien in JSON"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)
    logger.info(f"Kategorien gespeichert: {CONFIG_FILE}")


def add_category(name, keywords):
    """Fügt neue Kategorie hinzu"""
    categories = load_categories()
    categories[name] = [k.strip().lower() for k in keywords.split(',')]
    save_categories(categories)
    print(f"✅ Kategorie '{name}' hinzugefügt mit {len(categories[name])} Keywords")


def init_db():
    """Initialisiert die SQLite-Datenbank"""
    try:
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
        
        # Index für schnellere Abfragen
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON expenses(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON expenses(category)")
        
        conn.commit()
        conn.close()
        print(f"✅ Datenbank initialisiert: {DB_PATH}")
        logger.info("Datenbank initialisiert")
    except Exception as e:
        logger.error(f"Datenbank-Fehler: {e}")
        print(f"❌ Fehler: {e}")


def parse_amount(text):
    """Parst deutsche Beträge korrekt (1.234,56€)"""
    # Entferne Währungssymbole
    text = text.replace('€', '').replace('$', '')
    
    # Suche nach deutschem Format: 1.234,56 oder 12,50
    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', text)
    if match:
        amount_str = match.group(1).replace('.', '').replace(',', '.')
        return float(amount_str)
    
    # Suche nach einfachem Format: 12.50 oder 12,50
    match = re.search(r'(\d+[,.]\d{2})', text)
    if match:
        amount_str = match.group(1).replace(',', '.')
        return float(amount_str)
    
    # Suche nach ganzer Zahl
    match = re.search(r'(\d+)', text)
    if match:
        return float(match.group(1))
    
    return None


def detect_category(text, categories):
    """Erkennt Kategorie basierend auf Keywords"""
    text_lower = text.lower()
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return "Sonstiges"


def detect_store(text):
    """Erkennt den Händler/Supermarkt aus dem Text"""
    text_lower = text.lower()
    stores = ["rewe", "lidl", "aldi", "edeka", "kaufland", "penny", "netto", 
              "dm", "rossmann", "amazon", "ebay", "media markt", "saturn",
              "bäckerei", "apotheke", "arzt", "bahn", "db", "tankstelle",
              "mcdonalds", "burger king", "kfc", "subway", "pizzeria"]
    
    for store in stores:
        if store in text_lower:
            return store.title()
    
    return None


def check_duplicate(amount, description, store):
    """Prüft auf Duplikate (gleicher Betrag, Händler und Tag)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT COUNT(*) FROM expenses 
            WHERE amount = ? AND store = ? AND date LIKE ?
        """, (amount, store, f"{today}%"))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        logger.error(f"Duplikat-Prüfung fehlgeschlagen: {e}")
        return False


def add_expense(text):
    """Fügt eine Ausgabe hinzu"""
    amount = parse_amount(text)
    
    if amount is None:
        print("❌ Konnte keinen Betrag erkennen!")
        print("💡 Beispiel: 'Habe 12,50€ bei Rewe für Milch ausgegeben'")
        print("💡 Oder: '1.250,00€ für Miete'")
        return
    
    categories = load_categories()
    category = detect_category(text, categories)
    store = detect_store(text)
    
    # Beschreibung extrahieren (alles außer Betrag)
    description = re.sub(r'\d{1,3}(?:\.\d{3})*,\d{2}', '', text).strip()
    description = re.sub(r'\d+[,.]?\d*', '', description).strip()
    description = re.sub(r'\s+', ' ', description)
    
    # Duplikat-Check
    if check_duplicate(amount, description, store):
        print(f"⚠️  WARNUNG: Ähnliche Ausgabe ({amount:.2f}€ bei {store}) wurde HEUTE bereits eingetragen!")
        confirm = input("Trotzdem speichern? (j/n): ")
        if confirm.lower() not in ['j', 'ja', 'y', 'yes']:
            print("❌ Abgebrochen.")
            return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO expenses (amount, category, store, description, date)
            VALUES (?, ?, ?, ?, ?)
        """, (amount, category, store, description, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Ausgabe gespeichert:")
        print(f"   💰 {amount:.2f}€")
        print(f"   📂 {category}")
        if store:
            print(f"   🏪 {store}")
        if description:
            print(f"   📝 {description}")
        
        logger.info(f"Ausgabe gespeichert: {amount:.2f}€ - {category}")
    except Exception as e:
        logger.error(f"Speichern fehlgeschlagen: {e}")
        print(f"❌ Fehler beim Speichern: {e}")


def get_weekly_report():
    """Erstellt einen Bericht für die aktuelle Kalenderwoche"""
    try:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start_of_week.isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "📊 Keine Ausgaben diese Woche."
        
        total = sum(r[1] for r in results)
        
        report = [f"📊 **WÖCHENTLICHER AUSGABENBERICHT**\n"]
        report.append(f"Zeitraum: {start_of_week.strftime('%d.%m.%Y')} - {today.strftime('%d.%m.%Y')}")
        report.append(f"Gesamt: **{total:.2f}€**\n")
        report.append("Nach Kategorie:")
        
        for category, amount in results:
            percentage = (amount / total) * 100
            report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Wochenbericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_monthly_report():
    """Erstellt einen Bericht für den aktuellen Monat"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Nach Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start_of_month.isoformat(),))
        
        category_results = cursor.fetchall()
        
        # Nach Händler
        cursor.execute("""
            SELECT store, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND store IS NOT NULL
            GROUP BY store
            ORDER BY total DESC
            LIMIT 5
        """, (start_of_month.isoformat(),))
        
        store_results = cursor.fetchall()
        conn.close()
        
        if not category_results:
            return "📊 Keine Ausgaben diesen Monat."
        
        total = sum(r[1] for r in category_results)
        
        report = [f"📊 **MONATLICHER AUSGABENBERICHT**\n"]
        report.append(f"Monat: {today.strftime('%B %Y')}")
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
    except Exception as e:
        logger.error(f"Monatsbericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_store_comparison():
    """Vergleicht Ausgaben bei verschiedenen Händlern"""
    try:
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
    except Exception as e:
        logger.error(f"Händler-Vergleich fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def export_csv(filename=None):
    """Exportiert alle Daten als CSV"""
    if not filename:
        filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("📊 Keine Daten zum Exportieren.")
            return
        
        export_path = Path.home() / filename
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Betrag', 'Kategorie', 'Händler', 'Beschreibung', 'Datum', 'Erstellt'])
            writer.writerows(results)
        
        print(f"✅ Exportiert: {export_path}")
        logger.info(f"CSV exportiert: {export_path}")
    except Exception as e:
        logger.error(f"Export fehlgeschlagen: {e}")
        print(f"❌ Fehler: {e}")


def backup_db():
    """Erstellt ein Backup der Datenbank"""
    try:
        backup_file = f"{DB_PATH}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(DB_PATH, backup_file)
        logger.info(f"Backup erstellt: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"Backup fehlgeschlagen: {e}")
        return None


def list_expenses(limit=10):
    """Zeigt die letzten Einträge"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Summe
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total = cursor.fetchone()[0] or 0
        
        # Einträge
        cursor.execute("""
            SELECT date, amount, category, store, description 
            FROM expenses 
            ORDER BY date DESC 
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("📊 Keine Ausgaben vorhanden.")
            return
        
        print(f"📋 **Letzte {len(results)} Ausgaben:**")
        print(f"   💰 Gesamtsumme: {total:.2f}€\n")
        
        for date, amount, category, store, description in results:
            store_str = f" ({store})" if store else ""
            desc_str = f" - {description[:30]}" if description else ""
            print(f"  {date[:10]}: {amount:>8.2f}€ - {category}{store_str}{desc_str}")
    except Exception as e:
        logger.error(f"Auflisten fehlgeschlagen: {e}")
        print(f"❌ Fehler: {e}")


def main():
    parser = argparse.ArgumentParser(description="Expense Tracker - Ausgaben verfolgen")
    parser.add_argument("text", nargs="?", help="Ausgabe als Text (z.B. '12,50€ bei Rewe')")
    parser.add_argument("--init", action="store_true", help="Datenbank initialisieren")
    parser.add_argument("--weekly", action="store_true", help="Wöchentlicher Bericht")
    parser.add_argument("--monthly", action="store_true", help="Monatlicher Bericht")
    parser.add_argument("--stores", action="store_true", help="Händler-Vergleich")
    parser.add_argument("--list", action="store_true", help="Letzte Einträge anzeigen")
    parser.add_argument("--limit", type=int, default=10, help="Anzahl der Einträge (default: 10)")
    parser.add_argument("--add-category", metavar="NAME", help="Neue Kategorie hinzufügen")
    parser.add_argument("--keywords", help="Keywords für neue Kategorie (kommasepariert)")
    parser.add_argument("--export", action="store_true", help="Als CSV exportieren")
    parser.add_argument("--backup", action="store_true", help="Datenbank sichern")
    
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
        list_expenses(args.limit)
    elif args.add_category:
        if not args.keywords:
            print("❌ --keywords wird benötigt (z.B. --keywords 'gym,fitness,sport')")
            return
        add_category(args.add_category, args.keywords)
    elif args.export:
        export_csv()
    elif args.backup:
        backup_file = backup_db()
        if backup_file:
            print(f"✅ Backup erstellt: {backup_file}")
        else:
            print("❌ Backup fehlgeschlagen")
    elif args.text:
        add_expense(args.text)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
