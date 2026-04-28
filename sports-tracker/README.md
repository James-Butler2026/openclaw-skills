# Sports Tracker

Sport- und Fitness-Tracking mit Workout-Management, Kalorienberechnung und automatischer Auswertung.

## Features

- 🏃 **Aktivitäts-Tracking** – Spazieren, Fahrrad, P90X und mehr
- 🔥 **Kalorienberechnung** – Automatisch basierend auf MET-Werten und Gewicht
- 💪 **Workout-Management** – P90X/P90X2/P90X3 mit done/missed Status
- 📊 **Wochen-/Monatsberichte** – Übersichtliche Statistiken
- 🎯 **Sarkasmus-Modus** – Motivation bei verpassten Trainingstagen
- ⚖️ **Gewichts-Tracking** – Individuelles Gewicht für Kalorienberechnung

## Installation

```bash
# In den Skill-Ordner wechseln
cd sports-tracker/

# Datenbank initialisieren
python3 scripts/sports_tracker.py --init
```

## Verwendung

### Aktivität hinzufügen
```bash
# Spazieren
python3 scripts/sports_tracker.py --add "5 km Spazieren"

# Fahrrad
python3 scripts/sports_tracker.py --add "17.6 km Fahrrad"

# P90X
python3 scripts/sports_tracker.py --done P90X
```

### Berichte anzeigen
```bash
# Wochenbericht
python3 scripts/sports_tracker.py --week

# Monatsbericht
python3 scripts/sports_tracker.py --month

# Statistiken
python3 scripts/sports_tracker.py --stats
```

### Workout-Tracking
```bash
# Als erledigt markieren
python3 scripts/sports_tracker.py --done

# Als verpasst markieren
python3 scripts/sports_tracker.py --missed

# Workout-Status prüfen
python3 scripts/sports_tracker.py --workout-check
```

### Gewicht ändern
```bash
python3 scripts/sports_tracker.py --weight 118
```

## Kalorienberechnung

| Aktivität | MET | Ø Geschwindigkeit |
|-----------|-----|-------------------|
| Spazieren | 3.5 | 4.5 km/h |
| Fahrrad | 8.0 | 18 km/h |
| P90X | 6.0 | – |

**Formel:** `Kcal = MET × Gewicht(kg) × Dauer(h)`

## Datenbank

- **SQLite**-basiert
- Speicherort: `data/sports_tracker.db`
- Automatische Migration bei Updates

## Kirche des Bizeps 🏛️💪

> *"Ein Butler ist nur so gut wie sein letzter Curl."*

Bei verpassten Trainingstagen: Sarkasmus-Modus mit zufälligen Motivations-Sprüchen!

## Lizenz

MIT License – Für Eure Lordschaft und die Kirche des Bizeps.
