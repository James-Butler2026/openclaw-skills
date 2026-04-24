---
name: expense-tracker
description: Ausgaben-Tracking per Sprachnachricht mit automatischer Kategorie-Erkennung, Budget-Planung, Einkommen/Fixkosten-Verwaltung, Sparzielen, Trends, Spar-Tipps und Reports (wöchentlich/monatlich/jährlich)
version: 3.1
---

# Expense Tracker v3.1

Komplettes Budget-Tracking: Ausgaben per Sprachnachricht oder Text, automatische Kategorie-Erkennung, Einkommen, Fixkosten, Ersparnisse, Sparziele, Trends, Spar-Tipps und detaillierte Reports.

## 🆕 Neu in v3.1

- 📈 **Trend-Pfeile** – Vormonat-Vergleich mit ↑↓↔ Pfeilen
- 🎯 **Sparziele** – Ziele definieren mit Fortschrittsbalken
- 💡 **Spar-Tipps** – Automatische Empfehlungen basierend auf Ausgabenmuster
- ⚠️ **Budget-Warnungen** – Alarm bei 80% Budget-Auslastung
- 🔄 **Monatsvergleich** – Dieser Monat vs. Vormonat (oder x Monate zurück)
- 🏪 **Händler-Report** – Monats-Übersicht nach Händlern
- 🏷️ **Eigene Kategorien** – Neue Kategorien mit Keywords hinzufügen
- 💽 **Datenbank-Backup** – SQLite-Backup mit einem Befehl
- 📤 **CSV-Export** – Alle Daten als CSV exportieren

## 🆕 Neu in v3.0

- 💰 **Einkommen & Fixkosten** – Übergangsgeld, Miete, Versicherungen etc. in der DB
- 📊 **Budget-Übersicht** – Einkommen minus Fixkosten minus Variabel = Ersparnisse
- 📅 **Monatswochen** – 1.-7., 8.-14., 15.-21., 22.-Ende
- 📋 **Detail-Aufschlüsselung** – Einzelpositionen bei jedem Report
- 📆 **ISO-Kalenderwochen** – Montag bis Sonntag (deutscher Standard)
- 🗓️ **Jahresübersicht** – Alle Monate auf einen Blick
- 💾 **Monats-Zusammenfassungen** – Werden automatisch gespeichert
- 🔄 **Ersparnis-Tracking** – Pro Monat und gesamt
- ⏱️ **Temporäre Fixkosten** – Enddatum für Versicherungen die wegfallen
- 🔢 **Cent-genau** – Keine Rundung, immer exakte Beträge

## Features

- 🎤 **Spracheingabe**: *"Habe 12,50€ bei Rewe für Milch ausgegeben"*
- 🏷️ **Automatische Kategorien**: Erkennt Lebensmittel, Transport, Freizeit etc.
- 🏪 **Händler-Tracking**: Vergleicht Rewe vs Lidl vs Aldi
- 📊 **Reports**: Wöchentlich, monatlich, jährlich, gesamt
- 💰 **Budget-Planung**: Einkommen, Fixkosten, variable Ausgaben, Ersparnisse
- 📅 **Monatswochen**: 1.-7., 8.-14., 15.-21., 22.-Ende
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

### 3. Reports

#### Wöchentlich (ISO-KW, Mo-So)
```bash
python3 skills/expense-tracker/scripts/expense_tracker.py --weekly
python3 skills/expense-tracker/scripts/expense_tracker.py --last-week
```

#### Monatlich
```bash
# Variable Ausgaben 1. bis heute (mit Einzelposten)
python3 skills/expense-tracker/scripts/expense_tracker.py --month-to-date

# Vollständiger Monatsbericht mit Budget
python3 skills/expense-tracker/scripts/expense_tracker.py --monthly

# Kompletter Monat (speichert Zusammenfassung)
python3 skills/expense-tracker/scripts/expense_tracker.py --full-month
```

#### Jahr & Gesamt
```bash
# Jahresübersicht mit allen Monaten
python3 skills/expense-tracker/scripts/expense_tracker.py --year

# Gesamt-Übersicht aller Zeiten
python3 skills/expense-tracker/scripts/expense_tracker.py --total

# Ersparnisse pro Monat
python3 skills/expense-tracker/scripts/expense_tracker.py --savings
```

#### Analyse & Tools
```bash
# Trend-Pfeile (Vormonat-Vergleich)
python3 skills/expense-tracker/scripts/expense_tracker.py --trends

# Spar-Tipps (automatische Empfehlungen)
python3 skills/expense-tracker/scripts/expense_tracker.py --tips

# Sparziele mit Fortschrittsbalken
python3 skills/expense-tracker/scripts/expense_tracker.py --goals

# Budget-Warnungen bei 80%
python3 skills/expense-tracker/scripts/expense_tracker.py --budget-warnings

# Monatsvergleich (dieser vs. Vormonat)
python3 skills/expense-tracker/scripts/expense_tracker.py --compare

# Vergleich mit 3 Monate zurück
python3 skills/expense-tracker/scripts/expense_tracker.py --compare --months-back 3

# Händler-Report diesen Monat
python3 skills/expense-tracker/scripts/expense_tracker.py --stores-month
```

#### Verwaltung
```bash
# Letzte Einträge anzeigen
python3 skills/expense-tracker/scripts/expense_tracker.py --list
python3 skills/expense-tracker/scripts/expense_tracker.py --list --limit 20

# Eigene Kategorie hinzufügen
python3 skills/expense-tracker/scripts/expense_tracker.py --add-category "Streaming" --keywords "Netflix,Spotify,Disney"

# CSV Export
python3 skills/expense-tracker/scripts/expense_tracker.py --export

# Datenbank sichern
python3 skills/expense-tracker/scripts/expense_tracker.py --backup
```

## Datenbank-Struktur (v4.0)

### expenses
```sql
- id INTEGER PRIMARY KEY
- amount REAL NOT NULL        # Betrag (Cent-genau)
- category TEXT NOT NULL      # Kategorie
- store TEXT                  # Händler (optional)
- description TEXT           # Beschreibung
- date TEXT NOT NULL          # ISO-8601 Datum
- kw INTEGER                 # ISO-Kalenderwoche
- month_week INTEGER         # Monatswoche (1-4)
- created_at TEXT             # Timestamp
```

### income (Einnahmen)
```sql
- id INTEGER PRIMARY KEY
- name TEXT NOT NULL          # Name (z.B. "Übergangsgeld")
- amount REAL NOT NULL        # Betrag
- is_active INTEGER DEFAULT 1 # Aktiv?
- notes TEXT                  # Notizen
- created_at TEXT
```

### fixed_costs (Fixe Ausgaben)
```sql
- id INTEGER PRIMARY KEY
- name TEXT NOT NULL          # Name (z.B. "Miete")
- amount REAL NOT NULL        # Betrag
- category TEXT               # Kategorie
- is_active INTEGER DEFAULT 1 # Aktiv?
- end_date TEXT               # Enddatum (temporär) oder NULL
- notes TEXT                  # Notizen
- created_at TEXT
```

### monthly_summary (Monats-Zusammenfassungen)
```sql
- id INTEGER PRIMARY KEY
- year INTEGER NOT NULL
- month INTEGER NOT NULL
- total_income REAL           # Einkommen
- total_fixed REAL            # Fixkosten
- total_variable REAL         # Variable Ausgaben
- total_savings REAL          # Ersparnisse
- variable_by_category TEXT   # JSON mit Kategorien
- created_at TEXT
- UNIQUE(year, month)
```

## Automatische Kategorie-Erkennung

| Keyword | Kategorie |
|---------|-----------|
| Rewe, Lidl, Aldi, Edeka... | Lebensmittel |
| Bahn, DB, Bus, Tankstelle... | Transport |
| Kino, Restaurant, Netflix... | Freizeit |
| Amazon, Zalando, Media Markt... | Shopping |
| Schule, Bücher, Lernen... | Schule |
| Apotheke, Arzt, Sport... | Gesundheit |
| Crypto, Bitcoin, Krypto... | Anlagevermögen |

Eigene Kategorien hinzufügen:
```bash
python3 skills/expense-tracker/scripts/expense_tracker.py --add-category "Haustier" --keywords "Futter,Tierarzt,Zoo"
```

## Cron-Jobs

```bash
# Wöchentlicher Report (Sonntags 20:05)
5 20 * * 0 python3 skills/expense-tracker/scripts/expense_tracker.py --weekly

# Monats-Zusammenfassung (Letzter Tag des Monats)
0 20 28-31 * * python3 skills/expense-tracker/scripts/expense_tracker.py --full-month
```

---
*Expense Tracker v3.1 – Komplettes Budget-Tracking für Eure Lordschaft* 💰🎩