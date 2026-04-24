# AP1 Training Tracker

IHK Fachinformatiker AP1 Prüfungsvorbereitung – interaktiver Lern-Tracker mit 280 Multiple-Choice-Fragen in einer SQLite-Datenbank.

## Features

- **280 Fragen** aus 6 Themengebieten der IHK AP1 Prüfung
- **50 Subnetting-Fragen** – das wichtigste Thema extra trainieren
- **Interaktives Training** – Frage für Frage mit sofortigem Feedback
- **Automatische Statistiken** – wöchentlich, monatlich, gesamt
- **SQLite-basiert** – alle Daten lokal, keine Cloud, kein API-Key nötig
- **Keine Abhängigkeiten** – nur Python 3 Standardbibliothek

## Fragen-Übersicht

| Thema | Fragen | Inhalt |
|-------|--------|--------|
| IT-Grundlagen | 90 | Subnetting (50), Netzwerk, OSI/Hardware |
| Software-Entwicklung | 40 | OOP, Git, Debugging, Clean Code |
| Datenbanken | 40 | SQL, Normalisierung, ACID |
| IT-Sicherheit | 40 | VPN, 2FA, Verschlüsselung, Angriffe |
| Projektmanagement | 35 | Scrum, Gantt, Netzplan, Risiko |
| Wirtschaft | 35 | BWL, Steuern, Verträge, Marketing |

## Installation

```bash
# Skill-Ordner in den OpenClaw Workspace kopieren
cp -r ap1-training-tracker/ ~/openclaw-workspace/skills/

# Fertig – keine weiteren Abhängigkeiten
```

## Verwendung

### Interaktives Quiz starten

```bash
python3 skills/ap1-training-tracker/scripts/ap1_training.py --start
```

Startet ein Quiz mit 3 zufälligen Fragen. Nach jeder Frage wird die Antwort mit `--answer` übergeben.

### Antwort speichern

```bash
python3 skills/ap1-training-tracker/scripts/ap1_training.py --answer A
```

Wertet die Antwort für die aktuelle Frage aus und zeigt Ergebnis + Erklärung.

### Quiz-Status

```bash
python3 skills/ap1-training-tracker/scripts/ap1_training.py --status
```

Zeigt die aktuelle Frage, Fortschritt und bisherige Ergebnisse der laufenden Session.

### Quiz abbrechen

```bash
python3 skills/ap1-training-tracker/scripts/ap1_training.py --cancel
```

### Statistiken

```bash
# Wochenstatistik
python3 skills/ap1-training-tracker/scripts/ap1_training.py --stats

# Monatsstatistik
python3 skills/ap1-training-tracker/scripts/ap1_training.py --stats-month

# Gesamtstatistik
python3 skills/ap1-training-tracker/scripts/ap1_training.py --stats-all
```

### Tägliche 3 Fragen (klassisch)

```bash
python3 skills/ap1-training-tracker/scripts/ap1_training.py --daily
```

Gibt 3 Fragen auf einmal aus (ohne interaktiven Modus).

## Dateistruktur

```
ap1-training-tracker/
├── README.md
├── SKILL.md
├── data/
│   └── questions.db        # 280 Fragen in SQLite
└── scripts/
    ├── ap1_training.py     # Hauptscript (interaktiv)
    ├── ap1_tracker.py      # Tracker-Script
    └── shared_db.py        # Gemeinsame DB-Funktionen
```

## Interaktiver Modus in Python

```python
import sys
sys.path.insert(0, 'skills/ap1-training-tracker/scripts')
from ap1_training import start_quiz, answer_question, get_stats

# Quiz starten
questions = start_quiz(3)

# Antwort auswerten
result = answer_question(question_id='sub_001', answer='A')

# Statistik abrufen
stats = get_stats()
```

## Automatisierung mit OpenClaw Cron

```yaml
- name: ap1-training
  schedule:
    kind: cron
    expr: "30 9 * * *"
    tz: "Europe/Berlin"
  payload:
    kind: systemEvent
    text: "CRON_AP1_TRAINING"
  sessionTarget: main
```

Ablauf: Cron sendet Trigger → 3 Fragen nacheinander → User antwortet jeweils → Sofortiges Feedback mit Erklärung → Tagesabschluss mit Statistik.

## Beispielsession

```
📚 FRAGE 1/3
📱 IT-Grundlagen

❓ Wie viele Hosts hat ein /24-Netzwerk?
   A) 254    B) 256    C) 512    D) 1024

→ Antwort: A

✅ RICHTIG!
   /24 = 8 Host-Bits = 2^8 - 2 = 254 Hosts
   (Netz- und Broadcast-Adresse abziehen)

─────────────────────────────

📚 FRAGE 2/3
📱 Software-Entwicklung

❓ Was macht git commit?
   A) Sendet zum Server    B) Speichert lokal
   C) Löscht Dateien        D) Erstellt einen Branch

→ Antwort: B

✅ RICHTIG! git commit speichert Änderungen lokal.
```

## Tipps für die Prüfungsvorbereitung

1. **Täglich üben** – 3 Fragen dauern nur 2-3 Minuten
2. **Erklärungen lesen** – bei falschen Antworten die Begründung verstehen
3. **Schwächen identifizieren** – Statistik zeigt welche Themen Übung brauchen
4. **Subnetting wiederholen** – 50 Fragen für das wichtigste Thema
5. **Vor der Prüfung** – `--stats-all` für den Gesamtüberblick

## Voraussetzungen

- Python 3.8+
- Keine pip-Pakete nötig
- Keine Internetverbindung für die Fragen
- SQLite ist in Python integriert

## Lizenz

MIT