#!/usr/bin/env python3
"""
Expense Tracker v3.1 - Komplettes Budget-Tracking
Ausgaben-Tracking per Sprachnachricht
SQLite-basiert mit Reports, JSON-Konfiguration, Backup & CSV Export
Einkommen, Fixkosten, variable Ausgaben, Ersparnisse, Jahresübersicht
Budget-Warnungen, Trends, Spar-Tipps, Sparziele, Monatsvergleich
Budget-Ziele, Fortschrittsbalken, Trend-Pfeile, Händler-Report, Spartipps
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
import calendar
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


def calc_kw_and_month_week(dt):
    """Berechnet KW (ISO) und Monatswoche (1-4) für ein Datum"""
    kw = dt.isocalendar()[1]
    day = dt.day
    if day <= 7:
        month_week = 1
    elif day <= 14:
        month_week = 2
    elif day <= 21:
        month_week = 3
    else:
        month_week = 4
    return kw, month_week


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
        now = datetime.now()
        kw, month_week = calc_kw_and_month_week(now)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO expenses (amount, category, store, description, date, kw, month_week)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (amount, category, store, description, now.isoformat(), kw, month_week))
        
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


def _add_detail_lines(cursor, start_dt, end_dt, report, indent="   "):
    """Fügt Einzelpositionen zum Report hinzu, gruppiert nach Kategorie"""
    cursor.execute("""
        SELECT category, amount, store, description, date
        FROM expenses
        WHERE date >= ? AND date <= ?
        ORDER BY category, date
    """, (start_dt.isoformat(), end_dt.isoformat()))
    
    rows = cursor.fetchall()
    if not rows:
        return
    
    current_cat = None
    for cat, amount, store, desc, date in rows:
        if cat != current_cat:
            current_cat = cat
        date_str = date[:10] if date else "?"
        store_str = f" ({store})" if store else ""
        desc_str = f" – {desc[:40]}" if desc else ""
        report.append(f"{indent}{date_str}: {amount:>7.2f}€ {cat}{store_str}{desc_str}")


def get_weekly_report():
    """Erstellt einen Bericht für die aktuelle Kalenderwoche (Montag-Sonntag)"""
    try:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start_of_week.isoformat(), end_of_week.isoformat()))
        
        results = cursor.fetchall()
        
        if not results:
            conn.close()
            return "📊 Keine Ausgaben diese Woche."
        
        total = sum(r[1] for r in results)
        kw_num = today.isocalendar()[1]
        
        report = [f"📊 **WÖCHENTLICHER AUSGABENBERICHT – KW {kw_num}**\n"]
        report.append(f"Zeitraum: {start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}")
        report.append(f"Gesamt: **{total:.2f}€**\n")
        report.append("Nach Kategorie:")
        for category, amount in results:
            percentage = (amount / total) * 100
            report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        report.append(f"\n📋 **Einzelpositionen:**")
        _add_detail_lines(cursor, start_of_week, end_of_week, report)
        
        conn.close()
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Wochenbericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_monthly_report():
    """Erstellt einen Bericht für den aktuellen Monat mit Budget-Übersicht"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year = today.year
        month = today.month
        
        # Letzter Tag des Monats
        if month == 12:
            end_of_month = today.replace(year=year+1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=month+1, day=1) - timedelta(days=1)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # --- EINKOMMEN ---
        cursor.execute("SELECT name, amount FROM income WHERE is_active = 1")
        income_rows = cursor.fetchall()
        total_income = sum(r[1] for r in income_rows)
        
        # --- FIXE AUSGABEN ---
        current_date = today.strftime('%Y-%m-%d')
        cursor.execute("SELECT name, amount, category, end_date, notes FROM fixed_costs WHERE is_active = 1")
        fixed_rows = cursor.fetchall()
        total_fixed = 0
        fixed_by_cat = {}
        for name, amount, cat, end_date, notes in fixed_rows:
            if end_date and end_date < current_date:
                continue  # Abgelaufen
            total_fixed += amount
            if cat not in fixed_by_cat:
                fixed_by_cat[cat] = []
            fixed_by_cat[cat].append((name, amount, notes))
        
        # --- VARIABLE AUSGABEN (nach Kategorie) ---
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start_of_month.isoformat(),))
        category_results = cursor.fetchall()
        total_variable = sum(r[1] for r in category_results) if category_results else 0
        
        # --- VARIABLE AUSGABEN (nach Monatswoche) ---
        month_week_data = {}
        for mw in [1, 2, 3, 4]:
            if mw == 4:
                mw_start = today.replace(day=22)
                mw_end = end_of_month
            else:
                mw_start = today.replace(day=1 + (mw-1)*7)
                mw_end = today.replace(day=mw*7)
            
            cursor.execute("""
                SELECT SUM(amount) FROM expenses
                WHERE date >= ? AND date <= ?
            """, (mw_start.isoformat(), mw_end.replace(hour=23, minute=59, second=59).isoformat()))
            mw_total = cursor.fetchone()[0] or 0
            month_week_data[mw] = {
                'total': mw_total,
                'start': mw_start,
                'end': mw_end
            }
        
        # --- TOP HÄNDLER ---
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
        
        # --- REPORT ---
        report = [f"📊 **MONATLICHER BERICHT {today.strftime('%B %Y')}**\n"]
        
        # Einkommen
        report.append(f"💰 **Einkommen:** {total_income:.2f}€")
        for name, amount in income_rows:
            report.append(f"   • {name}: {amount:.2f}€")
        
        # Fixe Ausgaben
        report.append(f"\n🏠 **Fixe Ausgaben:** {total_fixed:.2f}€")
        for cat, items in sorted(fixed_by_cat.items()):
            report.append(f"   **{cat}:**")
            for name, amount, notes in items:
                note_str = f" ({notes})" if notes else ""
                report.append(f"   • {name}: {amount:.2f}€{note_str}")
        
        # Variable Ausgaben
        report.append(f"\n🛒 **Variable Ausgaben:** {total_variable:.2f}€")
        if category_results:
            for category, amount in category_results:
                percentage = (amount / total_variable) * 100 if total_variable > 0 else 0
                report.append(f"   • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        # Monatswochen
        report.append(f"\n📅 **Nach Monatswoche:**")
        for mw in [1, 2, 3, 4]:
            d = month_week_data[mw]
            report.append(f"   MW{mw} ({d['start'].strftime('%d.%m.')}-{d['end'].strftime('%d.%m.')}): {d['total']:.2f}€")
        
        # Top Händler
        if store_results:
            report.append(f"\n🏪 **Top Händler:**")
            for store, amount in store_results:
                report.append(f"   • {store}: {amount:.2f}€")
        
        # Zusammenfassung
        total_expenses = total_fixed + total_variable
        savings = total_income - total_expenses
        savings_pct = (savings / total_income * 100) if total_income > 0 else 0
        
        report.append(f"\n{'='*35}")
        report.append(f"📊 **Zusammenfassung:**")
        report.append(f"   Einkommen:    {total_income:>8.2f}€")
        report.append(f"   Fixkosten:   -{total_fixed:>8.2f}€")
        report.append(f"   Variabel:    -{total_variable:>8.2f}€")
        report.append(f"   {'─'*30}")
        if savings >= 0:
            report.append(f"   ✅ Übrig:     {savings:>8.2f}€ ({savings_pct:.1f}%)")
        else:
            report.append(f"   🔴 Defizit:  {savings:>8.2f}€ ({savings_pct:.1f}%)")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Monatsbericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_last_week_report():
    """Letzte Woche Montag-Sonntag (ISO KW)"""
    try:
        today = datetime.now()
        start_of_this_week = today - timedelta(days=today.weekday())
        start_of_last_week = start_of_this_week - timedelta(days=7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        start_dt = start_of_last_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = end_of_last_week.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start_dt.isoformat(), end_dt.isoformat()))
        
        results = cursor.fetchall()
        
        if not results:
            conn.close()
            return f"📊 Keine Ausgaben letzte Woche ({start_dt.strftime('%d.%m.%Y')} - {end_dt.strftime('%d.%m.%Y')})."
        
        total = sum(r[1] for r in results)
        kw_num = start_dt.isocalendar()[1]
        
        report = [f"📊 **LETZTE WOCHE (KW {kw_num})**\n"]
        report.append(f"Zeitraum: {start_dt.strftime('%d.%m.%Y')} - {end_dt.strftime('%d.%m.%Y')}")
        report.append(f"Gesamt: **{total:.2f}€**\n")
        
        for category, amount in results:
            percentage = (amount / total) * 100
            report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        report.append(f"\n📋 **Einzelpositionen:**")
        _add_detail_lines(cursor, start_dt, end_dt, report)
        
        conn.close()
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Letzte-Woche-Bericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_month_to_date_report():
    """Variable Ausgaben von 1. des Monats bis heute"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start_of_month.isoformat(), end_today.isoformat()))
        
        results = cursor.fetchall()
        
        if not results:
            conn.close()
            return f"📊 Keine Ausgaben bisher diesen Monat."
        
        total = sum(r[1] for r in results)
        
        report = [f"📊 **AUSGABEN BIS HEUTE ({start_of_month.strftime('%d.%m.')} - {today.strftime('%d.%m.%Y')})**\n"]
        report.append(f"Gesamt: **{total:.2f}€**\n")
        
        for category, amount in results:
            percentage = (amount / total) * 100
            report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        report.append(f"\n📋 **Einzelpositionen:**")
        _add_detail_lines(cursor, start_of_month, end_today, report)
        
        conn.close()
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Month-to-date fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_full_month_report(year=None, month=None):
    """Kompletter Monat (1. bis letzter Tag), nur variable Ausgaben, speichert Zusammenfassung in DB"""
    try:
        today = datetime.now()
        if year is None:
            year = today.year
        if month is None:
            month = today.month
        
        start = datetime(year, month, 1, 0, 0, 0)
        if month == 12:
            end = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Variable Ausgaben nach Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category
            ORDER BY total DESC
        """, (start.isoformat(), end.isoformat()))
        
        category_results = cursor.fetchall()
        total_variable = sum(r[1] for r in category_results) if category_results else 0
        
        # Nach Monatswoche
        month_week_data = {}
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        for mw, (d_start, d_end) in {
            1: (1, 7), 2: (8, 14), 3: (15, 21), 4: (22, last_day)
        }.items():
            mw_start = datetime(year, month, d_start, 0, 0, 0)
            mw_end = datetime(year, month, d_end, 23, 59, 59)
            cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= ? AND date <= ?",
                          (mw_start.isoformat(), mw_end.isoformat()))
            mw_total = cursor.fetchone()[0] or 0
            month_week_data[mw] = (mw_start, mw_end, mw_total)
        
        # Einkommen
        cursor.execute("SELECT SUM(amount) FROM income WHERE is_active = 1")
        total_income = cursor.fetchone()[0] or 0
        
        # Fixe Ausgaben (aktive, nicht abgelaufene)
        current_date = today.strftime('%Y-%m-%d')
        cursor.execute("SELECT SUM(amount) FROM fixed_costs WHERE is_active = 1 AND (end_date IS NULL OR end_date >= ?)", (start.strftime('%Y-%m-%d'),))
        total_fixed = cursor.fetchone()[0] or 0
        
        # Berechne Ersparnis
        total_savings = total_income - total_fixed - total_variable
        
        # In monthly_summary speichern (UPSERT)
        import json as _json
        cat_dict = {cat: amt for cat, amt in category_results} if category_results else {}
        
        cursor.execute("""
            INSERT INTO monthly_summary (year, month, total_income, total_fixed, total_variable, total_savings, variable_by_category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(year, month) DO UPDATE SET
                total_income = excluded.total_income,
                total_fixed = excluded.total_fixed,
                total_variable = excluded.total_variable,
                total_savings = excluded.total_savings,
                variable_by_category = excluded.variable_by_category
        """, (year, month, total_income, total_fixed, total_variable, total_savings, _json.dumps(cat_dict)))
        
        conn.commit()
        conn.close()
        
        # Report
        month_names = {1:'Januar',2:'Februar',3:'März',4:'April',5:'Mai',6:'Juni',
                       7:'Juli',8:'August',9:'September',10:'Oktober',11:'November',12:'Dezember'}
        month_name = month_names.get(month, str(month))
        
        report = [f"📊 **{month_name} {year} – VARIABLE AUSGABEN**\n"]
        report.append(f"Zeitraum: 01.{month:02d}.{year} - {last_day}.{month:02d}.{year}")
        report.append(f"Variable Ausgaben: **{total_variable:.2f}€**\n")
        
        if category_results:
            for category, amount in category_results:
                percentage = (amount / total_variable) * 100 if total_variable > 0 else 0
                report.append(f"  • {category}: {amount:.2f}€ ({percentage:.1f}%)")
        
        report.append(f"\n📅 **Nach Monatswoche:**")
        for mw in [1, 2, 3, 4]:
            mw_start, mw_end, mw_total = month_week_data[mw]
            report.append(f"   MW{mw} ({mw_start.strftime('%d.%m.')}-{mw_end.strftime('%d.%m.')}): {mw_total:.2f}€")
        
        report.append(f"\n{'='*35}")
        report.append(f"💰 Einkommen:       {total_income:>8.2f}€")
        report.append(f"🏠 Fixkosten:      -{total_fixed:>8.2f}€")
        report.append(f"🛒 Variabel:      -{total_variable:>8.2f}€")
        report.append(f"   {'─'*30}")
        if total_savings >= 0:
            report.append(f"✅ Gespart:         {total_savings:>8.2f}€")
        else:
            report.append(f"🔴 Defizit:       {total_savings:>8.2f}€")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Vollmonat-Bericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_savings_overview():
    """Übersicht aller gespeicherten Monats-Zusammenfassungen"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT year, month, total_income, total_fixed, total_variable, total_savings
            FROM monthly_summary
            ORDER BY year, month
        """)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "📊 Noch keine Monats-Zusammenfassungen vorhanden. Nutze --full-month um welche zu erstellen."
        
        month_names = {1:'Jan',2:'Feb',3:'Mär',4:'Apr',5:'Mai',6:'Jun',
                       7:'Jul',8:'Aug',9:'Sep',10:'Okt',11:'Nov',12:'Dez'}
        
        report = [f"📊 **ERSPARNISSE – ÜBERSICHT**\n"]
        report.append(f"{'Monat':>8s} | {'Eink.':>8s} | {'Fix':>8s} | {'Var.':>8s} | {'Gespart':>8s}")
        report.append(f"{'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}")
        
        total_saved = 0
        for y, m, inc, fix, var, sav in results:
            mon = f"{month_names.get(m, str(m))} {y}"
            report.append(f"{mon:>8s} | {inc:>7.0f}€ | {fix:>7.0f}€ | {var:>7.0f}€ | {sav:>7.0f}€")
            total_saved += sav
        
        report.append(f"\n💰 **Gesamt gespart: {total_saved:.2f}€**")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Savings-Übersicht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_yearly_report(year=None):
    """Jahresübersicht mit allen Monaten, Einkommen, Fixkosten, Variabel, Ersparnisse"""
    try:
        today = datetime.now()
        if year is None:
            year = today.year
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        month_names = {1:'Januar',2:'Februar',3:'März',4:'April',5:'Mai',6:'Juni',
                       7:'Juli',8:'August',9:'September',10:'Oktober',11:'November',12:'Dezember'}
        
        # Gespeicherte Monatszusammenfassungen
        cursor.execute("""
            SELECT month, total_income, total_fixed, total_variable, total_savings
            FROM monthly_summary WHERE year = ? ORDER BY month
        """, (year,))
        saved_months = {r[0]: r for r in cursor.fetchall()}
        
        # Aktuelle Einkommen/Fixkosten aus DB
        cursor.execute("SELECT SUM(amount) FROM income WHERE is_active = 1")
        income_monthly = cursor.fetchone()[0] or 0
        
        current_date = today.strftime('%Y-%m-%d')
        cursor.execute("SELECT SUM(amount) FROM fixed_costs WHERE is_active = 1 AND (end_date IS NULL OR end_date >= ?)", (f"{year}-01-01",))
        fixed_monthly = cursor.fetchone()[0] or 0
        
        # Alle variablen Ausgaben des Jahres
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses WHERE date >= ? AND date <= ?
            GROUP BY category ORDER BY total DESC
        """, (year_start.isoformat(), year_end.isoformat()))
        year_categories = cursor.fetchall()
        total_year_variable = sum(r[1] for r in year_categories) if year_categories else 0
        
        # Nach Monat aufschlüsseln
        cursor.execute("""
            SELECT strftime('%m', date) as mon, SUM(amount)
            FROM expenses WHERE date >= ? AND date <= ?
            GROUP BY mon ORDER BY mon
        """, (year_start.isoformat(), year_end.isoformat()))
        month_variable = {int(r[0]): r[1] for r in cursor.fetchall()}
        
        conn.close()
        
        # Report
        report = [f"📊 **JAHRESÜBERSICHT {year}**\n"]
        
        report.append(f"{'Monat':>10s} | {'Eink.':>8s} | {'Fix':>8s} | {'Var.':>8s} | {'Gespart':>8s}")
        report.append(f"{'─'*10}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}")
        
        year_income = 0
        year_fixed = 0
        year_variable = 0
        year_savings = 0
        
        for m in range(1, 13):
            if m > today.month and year == today.year:
                break
            
            mon_name = month_names.get(m, str(m))[:3]
            
            if m in saved_months:
                _, inc, fix, var, sav = saved_months[m]
            else:
                inc = income_monthly
                fix = fixed_monthly
                var = month_variable.get(m, 0)
                sav = inc - fix - var
            
            year_income += inc
            year_fixed += fix
            year_variable += var
            year_savings += sav
            
            report.append(f"{mon_name:>10s} | {inc:>7.0f}€ | {fix:>7.0f}€ | {var:>7.0f}€ | {sav:>7.0f}€")
        
        report.append(f"{'─'*10}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}")
        report.append(f"{'TOTAL':>10s} | {year_income:>7.0f}€ | {year_fixed:>7.0f}€ | {year_variable:>7.0f}€ | {year_savings:>7.0f}€")
        
        report.append(f"\n🛒 **Variable Ausgaben nach Kategorie ({year}):**")
        if year_categories:
            for cat, amount in year_categories:
                pct = (amount / total_year_variable * 100) if total_year_variable > 0 else 0
                report.append(f"  • {cat}: {amount:.2f}€ ({pct:.1f}%)")
        
        report.append(f"\n{'='*50}")
        report.append(f"💰 Einkommen:       {year_income:>10.2f}€")
        report.append(f"🏠 Fixkosten:      -{year_fixed:>10.2f}€")
        report.append(f"🛒 Variabel:      -{year_variable:>10.2f}€")
        report.append(f"   {'─'*40}")
        if year_savings >= 0:
            report.append(f"✅ Gespart:          {year_savings:>10.2f}€")
        else:
            report.append(f"🔴 Defizit:        {year_savings:>10.2f}€")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Jahresbericht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_total_overview():
    """Gesamtübersicht aller Zeiten - alle Monate zusammengerechnet"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Alle Ausgaben
        cursor.execute("SELECT MIN(date), MAX(date), SUM(amount), COUNT(*) FROM expenses")
        first_date, last_date, total_variable, count = cursor.fetchone()
        
        if not first_date:
            conn.close()
            return "📊 Noch keine Ausgaben erfasst."
        
        # Nach Kategorie
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC")
        categories = cursor.fetchall()
        
        # Alle gespeicherten Monatszusammenfassungen
        cursor.execute("""
            SELECT year, month, total_income, total_fixed, total_variable, total_savings
            FROM monthly_summary ORDER BY year, month
        """)
        saved = cursor.fetchall()
        
        # Einkommen & Fixkosten (aktuell)
        cursor.execute("SELECT SUM(amount) FROM income WHERE is_active = 1")
        income_monthly = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM fixed_costs WHERE is_active = 1")
        fixed_monthly = cursor.fetchone()[0] or 0
        
        conn.close()
        
        first_dt = datetime.fromisoformat(first_date)
        last_dt = datetime.fromisoformat(last_date)
        
        report = [f"📊 **GESAMT-ÜBERSICHT (aller Zeiten)**\n"]
        report.append(f"Zeitraum: {first_dt.strftime('%d.%m.%Y')} - {last_dt.strftime('%d.%m.%Y')}")
        report.append(f"{count} Ausgaben erfasst\n")
        
        # Variable Ausgaben gesamt
        report.append(f"🛒 **Variable Ausgaben gesamt: {total_variable:.2f}€**\n")
        for cat, amount in categories:
            pct = (amount / total_variable * 100) if total_variable > 0 else 0
            report.append(f"  • {cat}: {amount:.2f}€ ({pct:.1f}%)")
        
        # Monatszusammenfassungen
        if saved:
            month_names = {1:'Jan',2:'Feb',3:'Mär',4:'Apr',5:'Mai',6:'Jun',
                           7:'Jul',8:'Aug',9:'Sep',10:'Okt',11:'Nov',12:'Dez'}
            report.append(f"\n📅 **Monats-Zusammenfassungen:**")
            total_inc = total_fix = total_var = total_sav = 0
            for y, m, inc, fix, var, sav in saved:
                mon = f"{month_names.get(m, str(m))} {y}"
                report.append(f"  {mon}: Eink. {inc:.0f}€ | Fix {fix:.0f}€ | Var {var:.0f}€ | Gespart {sav:.0f}€")
                total_inc += inc
                total_fix += fix
                total_var += var
                total_sav += sav
            
            report.append(f"\n💰 **Gesamt über alle Monate:**")
            report.append(f"  Einkommen: {total_inc:.2f}€")
            report.append(f"  Fixkosten: {total_fix:.2f}€")
            report.append(f"  Variabel:  {total_var:.2f}€")
            if total_sav >= 0:
                report.append(f"  ✅ Gespart: {total_sav:.2f}€")
            else:
                report.append(f"  🔴 Defizit: {total_sav:.2f}€")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Gesamt-Übersicht fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def check_budget_warnings(threshold=0.8):
    """Prüft ob variable Ausgaben über X% des verfügbaren Budgets sind + pro Kategorie"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Einkommen & Fixkosten
        cursor.execute("SELECT SUM(amount) FROM income WHERE is_active = 1")
        total_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM fixed_costs WHERE is_active = 1 AND (end_date IS NULL OR end_date >= ?)", (today.strftime('%Y-%m-%d'),))
        total_fixed = cursor.fetchone()[0] or 0
        
        available_for_variable = total_income - total_fixed
        
        # Aktuelle variable Ausgaben
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= ? AND date <= ?", (start_of_month.isoformat(), end_today.isoformat()))
        total_variable = cursor.fetchone()[0] or 0
        
        # Nach Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses WHERE date >= ? AND date <= ?
            GROUP BY category ORDER BY total DESC
        """, (start_of_month.isoformat(), end_today.isoformat()))
        spending = {r[0]: r[1] for r in cursor.fetchall()}
        
        # Budget-Ziele pro Kategorie
        cursor.execute("SELECT category, monthly_limit FROM budget_goals WHERE is_active = 1 AND monthly_limit > 0 ORDER BY category")
        goals = {r[0]: r[1] for r in cursor.fetchall()}
        conn.close()
        
        # Gesamt-Variable-Budget prüfen
        var_pct = (total_variable / available_for_variable) if available_for_variable > 0 else 0
        var_bar_filled = min(int(var_pct * 10), 10)
        var_bar = "█" * var_bar_filled + "░" * (10 - var_bar_filled)
        var_emoji = "🔴" if var_pct >= 1.0 else ("🟡" if var_pct >= 0.9 else ("🟠" if var_pct >= threshold else "🟢"))
        
        avail_s = f"{available_for_variable:.2f}".replace('.', ',')
        var_s = f"{total_variable:.2f}".replace('.', ',')
        thresh_s = f"{available_for_variable * threshold:.2f}".replace('.', ',')
        
        report = [f"⚠️ **BUDGET-WARNUNGEN** ({today.strftime('%B %Y')})\n"]
        
        # Gesamt-Variable
        report.append(f"💰 **Verfügbares Budget (Einkommen – Fixkosten): {avail_s}€**")
        report.append(f"   {var_emoji} Variabel gesamt: {var_bar} {var_pct*100:.0f}% ({var_s}€ / {avail_s}€)")
        
        if var_pct >= threshold:
            report.append(f"\n   🔴 **WARNUNG: Variable Ausgaben bei {var_pct*100:.0f}% des verfügbaren Budgets!**")
            report.append(f"   ⚡ 80%-Grenze: {thresh_s}€ | Aktuell: {var_s}€")
        else:
            report.append(f"   ✅ Noch unter {threshold*100:.0f}% ({thresh_s}€)")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Budget-Warnung fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_savings_goals():
    """Zeigt Sparziele mit Fortschrittsbalken"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Einkommen & Fixkosten
        cursor.execute("SELECT SUM(amount) FROM income WHERE is_active = 1")
        total_income = cursor.fetchone()[0] or 0
        
        current_date = today.strftime('%Y-%m-%d')
        cursor.execute("SELECT SUM(amount) FROM fixed_costs WHERE is_active = 1 AND (end_date IS NULL OR end_date >= ?)", (current_date,))
        total_fixed = cursor.fetchone()[0] or 0
        
        # Variable Ausgaben diesen Monat
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= ? AND date <= ?",
                      (start_of_month.isoformat(), end_today.isoformat()))
        total_variable = cursor.fetchone()[0] or 0
        
        # Budget-Ziele pro Kategorie
        cursor.execute("SELECT category, monthly_limit FROM budget_goals WHERE is_active = 1 AND monthly_limit > 0 ORDER BY monthly_limit DESC")
        goals = cursor.fetchall()
        
        # Ausgaben nach Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses WHERE date >= ? AND date <= ?
            GROUP BY category
        """, (start_of_month.isoformat(), end_today.isoformat()))
        spending = {r[0]: r[1] for r in cursor.fetchall()}
        
        conn.close()
        
        report = [f"🎯 **SPARZIELE & BUDGET – {today.strftime('%B %Y')}**\n"]
        
        # Gesamt-Budget
        savings_goal = total_income - total_fixed  # Was übrig wäre ohne variable Ausgaben
        actual_savings = total_income - total_fixed - total_variable
        pct = (actual_savings / savings_goal * 100) if savings_goal > 0 else 0
        bar_filled = min(int(pct / 10), 10) if pct >= 0 else 0
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        emoji = "✅" if pct >= 100 else ("🟢" if pct >= 70 else ("🟡" if pct >= 40 else "🔴"))
        
        report.append(f"💰 **Monats-Budget:**")
        report.append(f"   Einkommen: {total_income:.2f}€")
        report.append(f"   Fixkosten: -{total_fixed:.2f}€")
        report.append(f"   Variabel: -{total_variable:.2f}€")
        report.append(f"   Übrig: {actual_savings:.2f}€ von {savings_goal:.2f}€ möglich")
        report.append(f"   {emoji} {bar} {pct:.0f}% gespart\n")
        
        # Sparziel-Balken
        report.append(f"🎯 **Kategorie-Budgets:**")
        if goals:
            for cat, limit in goals:
                spent = spending.get(cat, 0)
                pct = (spent / limit * 100) if limit > 0 else 0
                bar_filled = min(int(min(pct, 100) / 10), 10)
                bar = "█" * bar_filled + "░" * (10 - bar_filled)
                emoji = "🔴" if pct >= 100 else ("🟡" if pct >= 80 else "🟢")
                over = f" ⚠️ ÜBER LIMIT!" if pct >= 100 else ""
                report.append(f"   {emoji} {cat}: {bar} {pct:.0f}% ({spent:.2f}€ / {limit:.2f}€){over}")
        else:
            report.append("   Keine Budget-Ziele gesetzt. Nutze --set-budget zum Setzen.")
        
        # Budget-Warnungen
        warnings = check_budget_warnings()
        if warnings:
            report.append(f"\n⚠️ **Budget-Warnungen:**")
            for w in warnings:
                report.append(f"   {w}")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Sparziele fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_month_comparison(months_back=1):
    """Vergleicht aktuellen Monat mit dem Vormonat (Trend-Pfeile)"""
    try:
        today = datetime.now()
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Vormonat berechnen
        if today.month == 1:
            prev_month = today.replace(year=today.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            prev_month = today.replace(month=today.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Ende des Vormonats
        if prev_month.month == 12:
            prev_end = prev_month.replace(year=prev_month.year+1, month=1, day=1) - timedelta(seconds=1)
        else:
            prev_end = prev_month.replace(month=prev_month.month+1, day=1) - timedelta(seconds=1)
        
        end_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Aktueller Monat nach Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category ORDER BY SUM(amount) DESC
        """, (current_month.isoformat(), end_today.isoformat()))
        current = {r[0]: r[1] for r in cursor.fetchall()}
        
        # Vormonat nach Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category ORDER BY SUM(amount) DESC
        """, (prev_month.isoformat(), prev_end.isoformat()))
        prev = {r[0]: r[1] for r in cursor.fetchall()}
        
        conn.close()
        
        month_names = {1:'Januar',2:'Februar',3:'März',4:'April',5:'Mai',6:'Juni',
                       7:'Juli',8:'August',9:'September',10:'Oktober',11:'November',12:'Dezember'}
        
        current_total = sum(current.values())
        prev_total = sum(prev.values())
        diff_total = current_total - prev_total if prev_total > 0 else current_total
        
        report = [f"📊 **MONATSVERGLEICH**\n"]
        report.append(f"   {month_names[prev_month.month]} {prev_month.year}: {prev_total:.2f}€")
        report.append(f"   {month_names[current_month.month]} {current_month.year}: {current_total:.2f}€")
        
        if prev_total > 0:
            pct_change = (diff_total / prev_total * 100)
            if diff_total > 0:
                report.append(f"   ⬆️ +{diff_total:.2f}€ ({pct_change:+.1f}%)")
            elif diff_total < 0:
                report.append(f"   ⬇️ {diff_total:.2f}€ ({pct_change:+.1f}%)")
            else:
                report.append(f"   ➡️ Gleichbleibend")
        else:
            report.append(f"   (Keine Daten für Vormonat)")
        
        report.append(f"\n📊 **Nach Kategorie:**\n")
        
        all_cats = sorted(set(list(current.keys()) + list(prev.keys())))
        for cat in all_cats:
            cur = current.get(cat, 0)
            prv = prev.get(cat, 0)
            diff = cur - prv
            
            if prv > 0:
                if diff > 0:
                    arrow = "⬆️"
                elif diff < 0:
                    arrow = "⬇️"
                else:
                    arrow = "➡️"
                report.append(f"   {arrow} {cat}: {cur:.2f}€ (vormonat {prv:.2f}€, {diff:+.2f}€)")
            else:
                report.append(f"   🆕 {cat}: {cur:.2f}€ (neu)")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Monatsvergleich fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_monthly_store_report():
    """Monatlicher Händler-Report mit Ø-Betrag pro Besuch"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT store, SUM(amount) as total, COUNT(*) as visits, AVG(amount) as avg
            FROM expenses
            WHERE date >= ? AND date <= ? AND store IS NOT NULL
            GROUP BY store
            ORDER BY total DESC
        """, (start_of_month.isoformat(), end_today.isoformat()))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "📊 Keine Händler-Daten diesen Monat."
        
        total = sum(r[1] for r in results)
        total_visits = sum(r[2] for r in results)
        
        report = [f"🏪 **HÄNDLER-REPORT {today.strftime('%B %Y')}**\n"]
        report.append(f"Gesamt: {total:.2f}€ in {total_visits} Besuchen\n")
        report.append(f"{'Händler':<15} | {'Gesamt':>8} | {'Besuche':>7} | {'Ø/Besuch':>9}")
        report.append(f"{'─'*15}-+-{'─'*8}-+-{'─'*7}-+-{'─'*9}")
        
        for store, total_amt, visits, avg in results:
            pct = (total_amt / total * 100) if total > 0 else 0
            report.append(f"{store:<15} | {total_amt:>7.2f}€ | {visits:>5}x  | {avg:>7.2f}€")
        
        report.append(f"\n💡 **Tipp:** {results[0][0]} ist Dein Top-Händler ({results[0][1]:.2f}€/{results[0][2]}x)")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Händler-Report fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def set_budget_goal(category, limit):
    """Setzt ein Budget-Ziel für eine Kategorie"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO budget_goals (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit, is_active = 1
        """, (category, limit))
        
        conn.commit()
        conn.close()
        return f"✅ Budget-Ziel gesetzt: {category} → {limit:.2f}€/Monat"
    except Exception as e:
        logger.error(f"Budget-Ziel setzen fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_spending_tip():
    """Generiert einen Spartipp basierend auf Ausgabenmustern"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Top Kategorie
        cursor.execute("""
            SELECT category, SUM(amount) as total FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category ORDER BY total DESC LIMIT 1
        """, (start_of_month.isoformat(), end_today.isoformat()))
        top = cursor.fetchone()
        
        # Häufigster Händler
        cursor.execute("""
            SELECT store, COUNT(*) as visits FROM expenses
            WHERE date >= ? AND date <= ? AND store IS NOT NULL
            GROUP BY store ORDER BY visits DESC LIMIT 1
        """, (start_of_month.isoformat(), end_today.isoformat()))
        top_store = cursor.fetchone()
        
        # Ø Ausgabe pro Tag
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= ? AND date <= ?",
                      (start_of_month.isoformat(), end_today.isoformat()))
        total = cursor.fetchone()[0] or 0
        days = today.day
        daily_avg = total / days if days > 0 else 0
        
        # Budget-Ziele
        cursor.execute("SELECT category, monthly_limit FROM budget_goals WHERE is_active = 1 AND monthly_limit > 0 ORDER BY monthly_limit DESC")
        goals = cursor.fetchall()
        
        # Kategorien über Budget
        cursor.execute("""
            SELECT e.category, SUM(e.amount), bg.monthly_limit
            FROM expenses e
            JOIN budget_goals bg ON e.category = bg.category
            WHERE e.date >= ? AND e.date <= ? AND bg.is_active = 1 AND bg.monthly_limit > 0
            GROUP BY e.category
            ORDER BY (SUM(e.amount) / bg.monthly_limit) DESC
        """, (start_of_month.isoformat(), end_today.isoformat()))
        over_budget = cursor.fetchall()
        
        conn.close()
        
        tips = []
        
        if top:
            tips.append(f"💡 Höchste Ausgabenkategorie: **{top[0]}** mit {top[1]:.2f}€")
        
        if top_store:
            tips.append(f"🏪 Häufigster Händler: **{top_store[0]}** ({top_store[1]}x besucht)")
        
        tips.append(f"📊 Ø {daily_avg:.2f}€ pro Tag (in {days} Tagen)")
        
        if over_budget:
            for cat, spent, limit in over_budget:
                pct = spent / limit * 100
                if pct >= 100:
                    tips.append(f"🔴 **{cat}** ist ÜBER Budget! ({spent:.2f}€ / {limit:.2f}€ = {pct:.0f}%)")
                elif pct >= 80:
                    tips.append(f"🟡 **{cat}** fast am Limit ({spent:.2f}€ / {limit:.2f}€ = {pct:.0f}%)")
        
        # Projektion für Monatsende
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        projected = daily_avg * days_in_month
        tips.append(f"\n📈 Projektion Monatsende: {projected:.2f}€ (bei {daily_avg:.2f}€/Tag)")
        
        return "\n".join(tips)
    except Exception as e:
        logger.error(f"Spartipp fehlgeschlagen: {e}")
        return f"❌ Fehler: {e}"


def get_trends():
    """Trend-Pfeile: Vergleicht aktuellen Monat mit Vormonat"""
    try:
        today = datetime.now()
        cur_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year
        
        prev_start = datetime(prev_year, prev_month, 1, 0, 0, 0)
        if prev_month == 12:
            prev_end = datetime(prev_year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            prev_end = datetime(prev_year, prev_month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses
            WHERE date >= ? GROUP BY category ORDER BY SUM(amount) DESC
        """, (cur_start.isoformat(),))
        cur_data = {r[0]: r[1] for r in cursor.fetchall()}
        
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses
            WHERE date >= ? AND date <= ? GROUP BY category
        """, (prev_start.isoformat(), prev_end.isoformat()))
        prev_data = {r[0]: r[1] for r in cursor.fetchall()}
        
        conn.close()
        
        cur_total = sum(cur_data.values())
        prev_total = sum(prev_data.values())
        
        month_names = {1:'Januar',2:'Februar',3:'März',4:'April',5:'Mai',6:'Juni',
                       7:'Juli',8:'August',9:'September',10:'Oktober',11:'November',12:'Dezember'}
        
        cur_name = f"{month_names.get(today.month, '?')} {today.year}"
        prev_name = f"{month_names.get(prev_month, '?')} {prev_year}"
        
        report = [f"📈 **TRENDS – {cur_name} vs. {prev_name}**\n"]
        
        if not prev_data:
            report.append("📊 Erster Monat mit Daten – kein Vergleich möglich.")
            ct = f"{cur_total:.2f}".replace('.', ',')
            report.append(f"\nAktuelle Ausgaben: **{ct}€**")
            return "\n".join(report)
        
        all_cats = sorted(set(list(cur_data.keys()) + list(prev_data.keys())))
        
        for cat in all_cats:
            cur = cur_data.get(cat, 0)
            prev = prev_data.get(cat, 0)
            
            cur_s = f"{cur:.2f}".replace('.', ',')
            prev_s = f"{prev:.2f}".replace('.', ',')
            
            if prev == 0 and cur == 0:
                continue
            elif prev == 0:
                arrow = '🆕'
                diff_s = f"+{cur_s}€ NEU"
            elif cur == 0:
                arrow = '⬇️'
                diff_s = f"-{prev_s}€ WEG"
            else:
                diff = cur - prev
                pct = (diff / prev) * 100
                arrow = '⬆️' if diff > 0 else ('⬇️' if diff < 0 else '➡️')
                diff_s = f"{diff:+.2f}€ ({pct:+.0f}%)".replace('.', ',')
            
            report.append(f"   {arrow} {cat}: {cur_s}€ → {prev_s}€ ({diff_s})")
        
        diff_total = cur_total - prev_total
        pct_total = (diff_total / prev_total * 100) if prev_total > 0 else 0
        arrow_total = '⬆️' if diff_total > 0 else ('⬇️' if diff_total < 0 else '➡️')
        ct = f"{cur_total:.2f}".replace('.', ',')
        pt = f"{prev_total:.2f}".replace('.', ',')
        dt = f"{diff_total:+.2f}€ ({pct_total:+.0f}%)".replace('.', ',')
        
        report.append(f"\n   {arrow_total} **GESAMT:** {ct}€ → {pt}€ ({dt})")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Trends fehlgeschlagen: {e}")
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
    parser = argparse.ArgumentParser(description="Expense Tracker v3.1 - Komplettes Budget-Tracking")
    parser.add_argument("text", nargs="?", help="Ausgabe als Text (z.B. '12,50€ bei Rewe')")
    parser.add_argument("--init", action="store_true", help="Datenbank initialisieren")
    parser.add_argument("--weekly", action="store_true", help="Aktuelle Kalenderwoche (Mo-So)")
    parser.add_argument("--last-week", action="store_true", help="Letzte Woche (Mo-So)")
    parser.add_argument("--month-to-date", action="store_true", help="Variable Ausgaben 1. bis heute")
    parser.add_argument("--monthly", action="store_true", help="Vollständiger Monatsbericht mit Budget")
    parser.add_argument("--full-month", action="store_true", help="Kompletter Monat (speichert Zusammenfassung)")
    parser.add_argument("--year", action="store_true", help="Jahresübersicht mit allen Monaten")
    parser.add_argument("--total", action="store_true", help="Gesamt-Übersicht aller Zeiten")
    parser.add_argument("--savings", action="store_true", help="Ersparnis-Übersicht aller Monate")
    parser.add_argument("--stores-month", action="store_true", help="Händler-Report diesen Monat")
    parser.add_argument("--budget-warnings", action="store_true", help="Budget-Warnungen bei 80%")
    parser.add_argument("--trends", action="store_true", help="Trend-Pfeile (Vormonat-Vergleich)")
    parser.add_argument("--tips", action="store_true", help="Spar-Tipps")
    parser.add_argument("--goals", action="store_true", help="Sparziele mit Fortschrittsbalken")
    parser.add_argument("--compare", action="store_true", help="Monatsvergleich")
    parser.add_argument("--months-back", type=int, default=1, help="Monate zurück für Vergleich (default: 1)")
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
    elif args.last_week:
        print(get_last_week_report())
    elif args.month_to_date:
        print(get_month_to_date_report())
    elif args.monthly:
        print(get_monthly_report())
    elif args.full_month:
        print(get_full_month_report())
    elif args.year:
        print(get_yearly_report())
    elif args.total:
        print(get_total_overview())
    elif args.savings:
        print(get_savings_overview())
    elif args.stores_month:
        print(get_monthly_store_report())
    elif args.budget_warnings:
        print(check_budget_warnings())
    elif args.trends:
        print(get_trends())
    elif args.tips:
        print(get_spending_tip())
    elif args.goals:
        print(get_savings_goals())
    elif args.compare:
        print(get_month_comparison(args.months_back))
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
