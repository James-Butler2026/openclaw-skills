# 💰 Expense Tracker v3.1

Komplettes Budget-Tracking für OpenClaw: Ausgaben per Sprachnachricht oder Text, Einkommen, Fixkosten, Ersparnisse, Sparziele, Trends, Spar-Tipps und detaillierte Reports.

## ✨ Features

### Grundfunktionen
- 🎤 **Spracheingabe**: *"12,50€ bei Rewe ausgegeben"* – automatisch geparst
- 🏷️ **Automatische Kategorie-Erkennung** – Lebensmittel, Transport, Shopping etc.
- 🏪 **Händler-Tracking** – Vergleicht Rewe vs Lidl vs Aldi
- 💾 **SQLite** – Lokale Datenbank, keine Cloud, kein API-Key nötig

### Budget-Management
- 💰 **Einkommen & Fixkosten** – Übergangsgeld, Miete, Versicherungen etc.
- 📊 **Budget-Übersicht** – Einkommen – Fixkosten – Variabel = Ersparnisse
- ⏱️ **Temporäre Fixkosten** – Enddatum für Versicherungen die wegfallen
- 🔢 **Cent-genau** – Keine Rundung, immer exakte Beträge

### Reports & Analyse
- 📅 **ISO-Kalenderwochen** – Montag bis Sonntag (deutscher Standard)
- 📅 **Monatswochen** – 1.-7., 8.-14., 15.-21., 22.-Ende
- 📋 **Detail-Aufschlüsselung** – Einzelpositionen bei Bedarf
- 🗓️ **Jahresübersicht** – Alle Monate auf einen Blick
- 💾 **Monats-Zusammenfassungen** – Automatisch gespeichert
- 🔄 **Ersparnis-Tracking** – Pro Monat und gesamt

### 🆕 Neu in v3.1
- 📈 **Trend-Pfeile** – Vormonat-Vergleich mit ↑↓↔ Pfeilen
- 🎯 **Sparziele** – Ziele definieren mit Fortschrittsbalken
- 💡 **Spar-Tipps** – Automatische Empfehlungen basierend auf Ausgabenmuster
- ⚠️ **Budget-Warnungen** – Alarm bei 80% Budget-Auslastung
- 🔄 **Monatsvergleich** – Dieser Monat vs. Vormonat (oder x Monate zurück)
- 🏪 **Händler-Report** – Monats-Übersicht nach Händlern
- 🏷️ **Eigene Kategorien** – Neue Kategorien mit Keywords hinzufügen
- 💽 **Datenbank-Backup** – SQLite-Backup mit einem Befehl
- 📤 **CSV-Export** – Alle Daten als CSV exportieren

## 🚀 Schnellstart

```bash
cd ~/.openclaw/workspace/skills/expense-tracker/

# Datenbank initialisieren
python3 scripts/expense_tracker.py --init

# Ausgabe erfassen
python3 scripts/expense_tracker.py "12,50€ bei Rewe"
python3 scripts/expense_tracker.py "45 Euro bei Amazon für ein Buch"
```

## 📊 Reports

### Wöchentlich (ISO-KW, Mo-So)
```bash
python3 scripts/expense_tracker.py --weekly
python3 scripts/expense_tracker.py --last-week
```

### Monatlich
```bash
python3 scripts/expense_tracker.py --month-to-date    # 1. bis heute
python3 scripts/expense_tracker.py --monthly          # Budget-Bericht
python3 scripts/expense_tracker.py --full-month        # Speichert Zusammenfassung
```

### Jahr & Gesamt
```bash
python3 scripts/expense_tracker.py --year              # Jahresübersicht
python3 scripts/expense_tracker.py --total             # Alles zusammengerechnet
python3 scripts/expense_tracker.py --savings           # Ersparnisse pro Monat
```

### Analyse & Tools
```bash
python3 scripts/expense_tracker.py --trends            # Trend-Pfeile (↑↓↔)
python3 scripts/expense_tracker.py --tips              # Spar-Tipps
python3 scripts/expense_tracker.py --goals             # Sparziele + Fortschritt
python3 scripts/expense_tracker.py --budget-warnings  # 80% Warnungen
python3 scripts/expense_tracker.py --compare           # Monat vs. Vormonat
python3 scripts/expense_tracker.py --compare --months-back 3  # vs. 3 Monate zurück
python3 scripts/expense_tracker.py --stores-month      # Händler diesen Monat
```

### Verwaltung
```bash
python3 scripts/expense_tracker.py --list              # Letzte Einträge
python3 scripts/expense_tracker.py --list --limit 20   # Mehr Einträge
python3 scripts/expense_tracker.py --add-category "Streaming" --keywords "Netflix,Spotify,Disney"
python3 scripts/expense_tracker.py --export            # CSV Export
python3 scripts/expense_tracker.py --backup            # DB Backup
```

## 🗄️ Datenbank-Struktur

### expenses (Ausgaben)
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| id | INTEGER | Primary Key |
| amount | REAL | Betrag (Cent-genau) |
| category | TEXT | Kategorie |
| store | TEXT | Händler (optional) |
| description | TEXT | Beschreibung |
| date | TEXT | ISO-8601 Datum |
| kw | INTEGER | ISO-Kalenderwoche |
| month_week | INTEGER | Monatswoche (1-4) |

### income (Einnahmen)
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Name (z.B. "Übergangsgeld") |
| amount | REAL | Betrag |
| is_active | INTEGER | Aktiv? (1/0) |
| notes | TEXT | Notizen |

### fixed_costs (Fixe Ausgaben)
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Name (z.B. "Miete") |
| amount | REAL | Betrag |
| category | TEXT | Kategorie |
| is_active | INTEGER | Aktiv? (1/0) |
| end_date | TEXT | Enddatum (temporär) oder NULL |

### monthly_summary (Monats-Zusammenfassungen)
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| id | INTEGER | Primary Key |
| year | INTEGER | Jahr |
| month | INTEGER | Monat |
| total_income | REAL | Einkommen |
| total_fixed | REAL | Fixkosten |
| total_variable | REAL | Variable Ausgaben |
| total_savings | REAL | Ersparnisse |
| variable_by_category | TEXT | JSON mit Kategorien |

## 🏷️ Automatische Kategorie-Erkennung

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
python3 scripts/expense_tracker.py --add-category "Haustier" --keywords "Futter,Tierarzt,Zoo"
```

## 🔒 Datenschutz

- ✅ Alle Finanzdaten bleiben lokal
- ✅ Keine Cloud-Synchronisation
- ✅ Keine API-Keys nötig
- ✅ Rein lokale SQLite-Datenbank
- ✅ Backup-Funktion integriert

## ⏱️ Cron-Jobs (Empfohlen)

```bash
# Wöchentlicher Report (Sonntags 20:05)
5 20 * * 0 python3 skills/expense-tracker/scripts/expense_tracker.py --weekly

# Monats-Zusammenfassung (Letzter Tag des Monats)
0 20 28-31 * * python3 skills/expense-tracker/scripts/expense_tracker.py --full-month
```

---
*Expense Tracker v3.1 – Komplettes Budget-Tracking für OpenClaw* 💰🎩