# Expense Tracker v3.0

Komplettes Budget-Tracking: Ausgaben per Sprachnachricht, Einkommen, Fixkosten, Ersparnisse und detaillierte Reports.

## ✨ Features

- 🎤 **Spracheingabe**: *"12,50€ bei Rewe ausgegeben"*
- 💰 **Einkommen & Fixkosten** – Übergangsgeld, Miete, Versicherungen etc.
- 📊 **Budget-Übersicht** – Einkommen – Fixkosten – Variabel = Ersparnisse
- 📅 **ISO-Kalenderwochen** – Montag bis Sonntag (deutscher Standard)
- 📅 **Monatswochen** – 1.-7., 8.-14., 15.-21., 22.-Ende
- 📋 **Detail-Aufschlüsselung** – Einzelpositionen bei Bedarf
- 🗓️ **Jahresübersicht** – Alle Monate auf einen Blick
- 💾 **Monats-Zusammenfassungen** – Automatisch gespeichert
- 🔄 **Ersparnis-Tracking** – Pro Monat und gesamt
- ⏱️ **Temporäre Fixkosten** – Enddatum für Versicherungen die wegfallen
- 🔢 **Cent-genau** – Keine Rundung, immer exakte Beträge
- 🏷️ **Automatische Kategorie-Erkennung** – Lebensmittel, Tanken, Shopping etc.
- 🏪 **Händler-Tracking** – Rewe vs Lidl vs Aldi Vergleich
- 💾 **SQLite** – Lokale Datenbank, keine Cloud

## 🚀 Schnellstart

```bash
cd ~/.openclaw/workspace/skills/expense-tracker/

# Datenbank initialisieren
python3 scripts/expense_tracker.py --init

# Ausgabe erfassen
python3 scripts/expense_tracker.py "12,50€ bei Rewe"
```

## 📊 Reports

```bash
# Wöchentlich (ISO-KW, Mo-So)
python3 scripts/expense_tracker.py --weekly
python3 scripts/expense_tracker.py --last-week

# Monatlich
python3 scripts/expense_tracker.py --month-to-date    # 1. bis heute
python3 scripts/expense_tracker.py --monthly          # Budget-Bericht
python3 scripts/expense_tracker.py --full-month        # Speichert Zusammenfassung

# Jahr & Gesamt
python3 scripts/expense_tracker.py --year              # Jahresübersicht
python3 scripts/expense_tracker.py --total             # Alles zusammengerechnet
python3 scripts/expense_tracker.py --savings           # Ersparnisse pro Monat

# Sonstiges
python3 scripts/expense_tracker.py --stores            # Händler-Vergleich
python3 scripts/expense_tracker.py --list              # Letzte Einträge
python3 scripts/expense_tracker.py --export           # CSV Export
```

## 🔒 Datenschutz

- Alle Finanzdaten bleiben lokal
- Keine Cloud-Synchronisation
- Keine API-Keys nötig
- Rein lokale SQLite-Datenbank

---
*Ausgaben-Tracking für OpenClaw v3.0 💰🎩*