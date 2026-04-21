#!/usr/bin/env python3
"""
Expense Tracker - Ausgaben-Tracking per Sprachnachricht
SQLite-basiert mit Reports nach Zeit, Kategorie und Händler

WICHTIG: Datenbank bleibt erhalten! Schema unverändert:
  - id (INTEGER PRIMARY KEY AUTOINCREMENT)
  - amount (REAL NOT NULL)
  - category (TEXT NOT NULL)
  - store (TEXT)
  - description (TEXT)
  - date (TEXT NOT NULL)
  - created_at (TEXT DEFAULT CURRENT_TIMESTAMP)
"""

import os
import sys
import re
import sqlite3
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Datenbank-Pfad (flexibel)
DB_PATH = Path(os.getenv('OPENCLAW_WORKSPACE', '/home/node/.openclaw/workspace')) / 'data' / 'expenses.db'

# Konfigurationsdatei für Kategorien
CONFIG_DIR = Path(__file__).parent.parent / 'config'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CATEGORIES_FILE = CONFIG_DIR / 'categories.json'

# Standard-Kategorien (werden bei erstmaligem Start gespeichert)
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

def load_categories() -> Dict[str, List[str]]:
    """Lädt Kategorien aus JSON oder erstellt Standard-Datei"""
    if CATEGORIES_FILE.exists():
        try:
            with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Laden der Kategorien: {e}")
    
    # Erstelle Standard-Datei
    save_categories(DEFAULT_CATEGORIES)
    return DEFAULT_CATEGORIES

def save_categories(categories: Dict[str, List[str]]):
    """Speichert Kategorien in JSON-Datei"""
    try:
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        logger.info(f"Kategorien gespeichert: {CATEGORIES_FILE}")
    except IOError as e:
        logger.error(f"Konnte Kategorien nicht speichern: {e}")

def init_db():
    """Initialisiert die SQLite-Datenbank (Schema bleibt identisch!)"""
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
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
        
        logger.info(f"✅ Datenbank bereit: {DB_PATH}")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Datenbank-Fehler: {e}")
        return False

def detect_category(text: str, categories: Dict[str, List[str]] = None) -> str:
    """Erkennt Kategorie basierend auf Keywords"""
    if categories is None:
        categories = load_categories()
    
    text_lower = text.lower()
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return "Sonstiges"

def detect_store(text: str) -> Optional[str]:
    """Erkennt den Händler/Supermarkt aus dem Text"""
    text_lower = text.lower()
    stores = [
        "rewe", "lidl", "aldi", "edeka", "kaufland", "penny", "netto", 
        "dm", "rossmann", "amazon", "ebay", "media markt", "saturn",
        "bäckerei", "apotheke", "arzt", "bahn", "db", "tankstelle",
        "shell", "aral", "avia", "esso", "lidl", "aldi"
    ]
    
    for store in stores:
        if store in text_lower:
            return store.title()
    
    return None

def parse_amount(text: str) -> Optional[float]:
    """Parst Betrag aus Text (robustere Erkennung)"""
    # Verschiedene Formate erkennen
    patterns = [
        r'(\d+[,.]\d{2})\s*[€$]?',           # 12,50 oder 12.50
        r'(\d+)\s*[€$]?',                       # 12 (ohne Dezimal)
        r'(\d+)\s*(?:Euro|EUR)',                # 12 Euro
        r'(\d+[,.]\d{2})\s*(?:Euro|EUR)',     # 12,50 Euro
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '.')
            try:
                return float(amount_str)
            except ValueError:
                continue
    
    return None

def parse_expense(text: str) -> Optional[Dict]:
    """Parst eine Ausgaben-Sprachnachricht"""
    amount = parse_amount(text)
    if amount is None:
        return None
    
    # Kategorie erkennen
    category = detect_category(text)
    
    # Händler erkennen
    store = detect_store(text)
    
    # Beschreibung extrahieren (alles außer Betrag)
    description = re.sub(r'\d+[,.]?\d*\s*[€$EUR]?', '', text, flags=re.IGNORECASE).strip()
    description = re.sub(r'\s+', ' ', description)  # Mehrfache Leerzeichen entfernen
    
    return {
        "amount": amount,
        "category": category,
        "store": store,
        "description": description
    }

def add_expense(text: str) -> bool:
    """Fügt eine Ausgabe hinzu (mit Error Handling)"""
    try:
        data = parse_expense(text)
        
        if not data:
            print("❌ Konnte keinen Betrag erkennen!")
            print("💡 Beispiel: 'Habe 12,50€ bei Rewe für Milch ausgegeben'")
            return False
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO expenses (amount, category, store, description, date)
                VALUES (?, ?, ?, ?, ?)
            """, (data["amount"], data["category"], data["store"], 
                  data["description"], datetime.now().isoformat()))
            
            conn.commit()
        
        print(f"✅ Ausgabe gespeichert:")
        print(f"   💰 {data['amount']:.2f}€")
        print(f"   📂 {data['category']}")
        if data['store']:
            print(f"   🏪 {data['store']}")
        if data['description']:
            print(f"   📝 {data['description']}")
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Datenbank-Fehler beim Speichern: {e}")
        print(f"❌ Fehler beim Speichern: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {e}")
        print(f"❌ Fehler: {e}")
        return False

def get_weekly_report() -> str:
    """Erstellt einen wöchentlichen Bericht (aktuelle Kalenderwoche Mo-So)"""
    try:
        today = datetime.now()
        # Aktuelle Woche: Montag bis Sonntag
        monday = today - timedelta(days=today.weekday())  # 0=Montag
        monday_iso = monday.replace(hour=0, minute=0, second=0).isoformat()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE date >= ?
                GROUP BY category
                ORDER BY total DESC
            """, (monday_iso,))
            
            results = cursor.fetchall()
        
        if not results:
            return f"📊 Keine Ausgaben diese Woche (ab {monday.strftime('%d.%m.%Y')})."
        
        total = sum(r[1] for r in results)
        
        report = [f"📊 **WÖCHENTLICHER AUSGABENBERICHT**\n"]
        report.append(f"Zeitraum: {monday.strftime('%d.%m.')} - {today.strftime('%d.%m.%Y')}\n")
        report.append(f"Gesamt: **{total:.2f}€**\n")
        report.append("Nach Kategorie:")
        
        for category, amount in results:
            percentage = (amount / total) * 100 if total > 0 else 0
            report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        return "\n".join(report)
        
    except sqlite3.Error as e:
        logger.error(f"❌ Fehler beim wöchentlichen Report: {e}")
        return f"❌ Fehler: {e}"

def get_monthly_report() -> str:
    """Erstellt einen monatlichen Bericht (aktueller Monat 1.-31.)"""
    try:
        today = datetime.now()
        # Erster Tag des aktuellen Monats
        first_day = today.replace(day=1, hour=0, minute=0, second=0)
        first_day_iso = first_day.isoformat()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Nach Kategorie
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE date >= ?
                GROUP BY category
                ORDER BY total DESC
            """, (first_day_iso,))
            
            category_results = cursor.fetchall()
            
            # Nach Händler
            cursor.execute("""
                SELECT store, SUM(amount) as total
                FROM expenses
                WHERE date >= ? AND store IS NOT NULL
                GROUP BY store
                ORDER BY total DESC
                LIMIT 5
            """, (first_day_iso,))
            
            store_results = cursor.fetchall()
        
        if not category_results:
            return f"📊 Keine Ausgaben diesen Monat ({today.strftime('%B %Y')})."
        
        total = sum(r[1] for r in category_results)
        
        report = [f"📊 **MONATLICHER AUSGABENBERICHT**\n"]
        report.append(f"Zeitraum: {today.strftime('%B %Y')}\n")
        report.append(f"Gesamt: **{total:.2f}€**\n")
        
        report.append("Nach Kategorie:")
        for category, amount in category_results:
            percentage = (amount / total) * 100 if total > 0 else 0
            report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        if store_results:
            report.append("\nTop Händler:")
            for store, amount in store_results:
                report.append(f"  • {store}: {amount:.2f}€")
        
        return "\n".join(report)
        
    except sqlite3.Error as e:
        logger.error(f"❌ Fehler beim monatlichen Report: {e}")
        return f"❌ Fehler: {e}"

def get_store_comparison() -> str:
    """Vergleicht Ausgaben bei verschiedenen Händlern"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT store, SUM(amount) as total, COUNT(*) as visits
                FROM expenses
                WHERE store IS NOT NULL
                GROUP BY store
                ORDER BY total DESC
            """)
            
            results = cursor.fetchall()
        
        if not results:
            return "📊 Keine Händler-Daten vorhanden."
        
        report = [f"🏪 **HÄNDLER-VERGLEICH**\n"]
        
        for store, total, visits in results:
            avg_per_visit = total / visits if visits > 0 else 0
            report.append(f"  • {store}: {total:.2f}€ ({visits}x, Ø {avg_per_visit:.2f}€)")
        
        return "\n".join(report)
        
    except sqlite3.Error as e:
        logger.error(f"❌ Fehler beim Händler-Vergleich: {e}")
        return f"❌ Fehler: {e}"

def get_recent_expenses(limit: int = 10) -> str:
    """Zeigt die letzten N Ausgaben"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, amount, category, store FROM expenses ORDER BY date DESC LIMIT ?",
                (limit,)
            )
            results = cursor.fetchall()
        
        if not results:
            return "📊 Keine Ausgaben vorhanden."
        
        report = [f"📋 **Letzte {limit} Ausgaben:**"]
        for date, amount, category, store in results:
            store_str = f" ({store})" if store else ""
            report.append(f"  {date[:10]}: {amount:.2f}€ - {category}{store_str}")
        
        return "\n".join(report)
        
    except sqlite3.Error as e:
        logger.error(f"❌ Fehler beim Abrufen: {e}")
        return f"❌ Fehler: {e}"

def add_category(category: str, keywords: List[str]) -> bool:
    """Fügt neue Kategorie mit Keywords hinzu"""
    try:
        categories = load_categories()
        
        if category in categories:
            # Keywords erweitern
            categories[category].extend([k for k in keywords if k not in categories[category]])
        else:
            categories[category] = keywords
        
        save_categories(categories)
        print(f"✅ Kategorie '{category}' hinzugefügt/erweitert")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Hinzufügen der Kategorie: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Expense Tracker - Ausgaben verfolgen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s "12,50€ bei Rewe"
  %(prog)s --weekly
  %(prog)s --monthly
        """
    )
    parser.add_argument("text", nargs="?", help="Ausgabe als Text")
    parser.add_argument("--init", action="store_true", help="Datenbank initialisieren")
    parser.add_argument("--weekly", action="store_true", help="Wöchentlicher Bericht")
    parser.add_argument("--monthly", action="store_true", help="Monatlicher Bericht")
    parser.add_argument("--stores", action="store_true", help="Händler-Vergleich")
    parser.add_argument("--list", action="store_true", help="Letzte 10 Einträge")
    parser.add_argument("--add-category", metavar="NAME", help="Neue Kategorie hinzufügen")
    parser.add_argument("--keywords", metavar="LIST", help="Keywords für neue Kategorie (komma-getrennt)")
    
    args = parser.parse_args()
    
    # Datenbank initialisieren (falls noch nicht geschehen)
    if args.init:
        init_db()
        return
    
    # Stelle sicher, dass DB existiert
    if not DB_PATH.exists():
        print("⚠️  Datenbank existiert noch nicht. Initialisiere...")
        if not init_db():
            sys.exit(1)
    
    if args.weekly:
        print(get_weekly_report())
    elif args.monthly:
        print(get_monthly_report())
    elif args.stores:
        print(get_store_comparison())
    elif args.list:
        print(get_recent_expenses())
    elif args.add_category:
        if not args.keywords:
            print("❌ --keywords erforderlich für --add-category")
            sys.exit(1)
        keywords = [k.strip() for k in args.keywords.split(',')]
        add_category(args.add_category, keywords)
    elif args.text:
        success = add_expense(args.text)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
