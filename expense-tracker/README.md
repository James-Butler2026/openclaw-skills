# 💰 Expense Tracker

Ausgaben-Tracking per Sprachnachricht mit automatischer Kategorie-Erkennung und Reports (wöchentlich/monatlich).

## Features

- 🎤 **Spracheingabe**: *"Habe 12,50€ bei Rewe für Milch ausgegeben"*
- 🏷️ **Automatische Kategorien**: Erkennt Lebensmittel, Transport, Freizeit etc.
- 🏪 **Händler-Tracking**: Vergleicht Rewe vs Lidl vs Aldi
- 📊 **Reports**: Wöchentlich & Monatlich automatisch
- 💾 **SQLite**: Lokale Datenbank, keine Cloud

## Schnellstart

### 1. Datenbank initialisieren
```bash
python3 skills/expense-tracker/scripts/expense_tracker.py --init
```

### 2. Ausgabe hinzufügen
```bash
# Per Text
python3 skills/expense-tracker/scripts/expense_tracker.py "12,50€ bei Rewe"

# Per Sprachnachricht (wird automatisch geparst)
"Habe 45 Euro bei Amazon für ein Buch ausgegeben"
```

### 3. Reports anzeigen
```bash
# Wöchentlich
python3 skills/expense-tracker/scripts/expense_tracker.py --weekly

# Monatlich (mit Händler-Top-5)
python3 skills/expense-tracker/scripts/expense_tracker.py --monthly

# Händler-Vergleich
python3 skills/expense-tracker/scripts/expense_tracker.py --stores

# Letzte 10 Einträge
python3 skills/expense-tracker/scripts/expense_tracker.py --list
```

## Automatische Erkennung

### Kategorien
| Keyword | Kategorie |
|---------|-----------|
| Rewe, Lidl, Aldi, Edeka... | Lebensmittel |
| Bahn, DB, Bus, Tankstelle... | Transport |
| Kino, Restaurant, Netflix... | Freizeit |
| Amazon, Zalando, Media Markt... | Shopping |
| Schule, Bücher, Lernen... | Schule |
| Apotheke, Arzt, Sport... | Gesundheit |

### Beispiele
```
"Habe 23,40€ bei Rewe für Lebensmittel ausgegeben"
→ 23.40€, Lebensmittel, Rewe

"Bahn-Ticket gekostet 18,50"
→ 18.50€, Transport, Bahn

"Bei Amazon 45 Euro für Bücher"
→ 45.00€, Shopping, Amazon
```

## In Python nutzen

```python
from skills.expense_tracker.scripts.expense_tracker import add_expense, get_monthly_report

# Ausgabe hinzufügen
add_expense("12,50€ bei Lidl")

# Report abrufen
report = get_monthly_report()
print(report)
```

## Cron-Job für automatische Reports

```bash
# Wöchentlich (Sonntags 20:00)
0 20 * * 0 python3 skills/expense-tracker/scripts/expense_tracker.py --weekly

# Monatlich (Letzter Tag des Monats)
0 20 28-31 * * [ $(date +\%m -d tomorrow) != $(date +\%m) ] && python3 skills/expense-tracker/scripts/expense_tracker.py --monthly
```

## Datenbank

**Pfad:** `~/.openclaw/workspace/data/expenses.db`

**Struktur:**
```sql
expenses:
- id (INTEGER PRIMARY KEY)
- amount (REAL)           # Betrag
- category (TEXT)           # Kategorie
- store (TEXT)            # Händler (optional)
- description (TEXT)      # Beschreibung
- date (TEXT)             # ISO-8601 Datum
- created_at (TEXT)       # Timestamp
```

---
*Skill erstellt für Eure Lordschaft* 🎩
