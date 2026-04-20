# Expense Tracker Skill

Ausgaben-Tracking per Spracheingabe mit automatischer Kategorie-Erkennung.

## Features

- 🎤 Spracheingabe: "12,50€ bei Rewe ausgegeben"
- 🏷️ Automatische Kategorie-Erkennung
- 🏪 Händler-Tracking
- 📊 Wöchentliche & monatliche Reports
- 💾 SQLite-basiert

## Installation

```bash
cd ~/.openclaw/workspace/skills/expense-tracker/
```

## Verwendung

```bash
# Ausgabe erfassen
python3 scripts/expense_tracker.py "12,50€ bei Rewe"

# Wöchentlicher Report
python3 scripts/expense_tracker.py --weekly

# Monatlicher Report
python3 scripts/expense_tracker.py --monthly

# Alle Ausgaben anzeigen
python3 scripts/expense_tracker.py --list
```

## Konfiguration

Keine API-Keys nötig – rein lokale SQLite-Datenbank.

## Sicherheit

- Alle Finanzdaten bleiben lokal
- Keine Cloud-Synchronisation
- Datenschutzfreundlich

---
*Ausgaben-Tracking für OpenClaw* 💰
