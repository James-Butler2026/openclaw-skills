---
name: sports-tracker
description: Sport- und Fitness-Tracking mit P90X, Spazieren und Fahrrad. SQLite-basiert mit Berichten (Woche, Monat), Emoji-Visualisierung, Kalorien-Berechnung und Workout-Tracking. Use when tracking sport activities, generating weekly/monthly fitness reports, logging workouts, or managing P90X workout schedules.
---

# Sports Tracker v2.0

Track P90X workouts, walks (Spazieren), bike rides (Fahrrad) with SQLite, CLI reports, automatic calorie calculation, and workout status tracking.

## CLI Usage

```bash
# Initialize / migrate database (safe to run on existing DB)
python3 skills/sports-tracker/scripts/sports_tracker.py --init

# ─── Add activities (auto-calculates calories) ───
python3 skills/sports-tracker/scripts/sports_tracker.py --add "5 km Spazieren"
python3 skills/sports-tracker/scripts/sports_tracker.py --add "P90X"
python3 skills/sports-tracker/scripts/sports_tracker.py --add "P90X 45 min"        # with custom duration
python3 skills/sports-tracker/scripts/sports_tracker.py --add "17.7 km Fahrrad"
python3 skills/sports-tracker/scripts/sports_tracker.py --add "4.24 km Spazieren gestern"

# ─── Weight management ───
python3 skills/sports-tracker/scripts/sports_tracker.py --weight 115

# ─── Reports ───
python3 skills/sports-tracker/scripts/sports_tracker.py --week       # Current week (Mon-Sun)
python3 skills/sports-tracker/scripts/sports_tracker.py --month      # 1st to today
python3 skills/sports-tracker/scripts/sports_tracker.py --month-full # Full month
python3 skills/sports-tracker/scripts/sports_tracker.py --list     # Last 10 entries with calories
python3 skills/sports-tracker/scripts/sports_tracker.py --stats      # Detailed stats (calories per activity)

# ─── Workout Tracking (P90X) ───
python3 skills/sports-tracker/scripts/sports_tracker.py --done              # Mark today as done (default: P90X)
python3 skills/sports-tracker/scripts/sports_tracker.py --done P90X3          # Mark as P90X3
python3 skills/sports-tracker/scripts/sports_tracker.py --missed              # Mark today as missed
python3 skills/sports-tracker/scripts/sports_tracker.py --workout-status    # Last 14 days status
python3 skills/sports-tracker/scripts/sports_tracker.py --workout-check       # JSON: training_day, done, missed_days, sarcasm
python3 skills/sports-tracker/scripts/sports_tracker.py --workout-stats       # Streaks, missed days, sarcasm
```

## Categories

| Category | Value type | Type | Emoji |
|----------|-----------|------|-------|
| P90X     | done (session count) | strength | 💪 |
| Spazieren| km        | cardio | 🚶 |
| Fahrrad  | km        | cardio | 🚴 |

## Calorie Calculation (Automatic)

Formula: `Kcal = MET × weight_kg × duration_hours`

| Activity | MET | Speed | Duration Calculation |
|----------|-----|-------|---------------------|
| Fahrrad  | 8.0 | 18 km/h | `km / 18` hours |
| Spazieren| 3.5 | 4.5 km/h | `km / 4.5` hours |
| P90X     | 6.0 | — | 60 min (default) or specified |

**Default weight:** 120 kg (configurable via `--weight`)

## Database

Path: `/home/node/.openclaw/workspace/data/sports_tracker.db`

### Tables

**activities** (main tracking)

| Column      | Type    | Description |
|-------------|---------|-------------|
| id          | INTEGER | Primary key |
| date        | TEXT    | Activity date |
| category    | TEXT    | P90X, Spazieren, Fahrrad |
| value       | TEXT    | km or "done" |
| description | TEXT    | Activity description |
| created_at  | TEXT    | Timestamp |
| type        | TEXT    | 'cardio' or 'strength' |
| duration_min| INTEGER | Duration in minutes |
| calories    | INTEGER | Calculated calories |
| speed_kmh   | REAL    | Average speed |
| weight_kg   | REAL    | Weight at time of activity |

**workout_status** (P90X tracking)

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | Unique date |
| is_training_day | BOOLEAN | Mo/We/Fr = true |
| status | TEXT | done, missed, rest, pending |
| type | TEXT | P90X, P90X2, P90X3 |
| notes | TEXT | Notes |

**user_settings** (key/value store)

| Key | Default | Description |
|-----|---------|-------------|
| weight_kg | 120 | Current weight |

## Workout Rules

- **Training days:** Monday, Wednesday, Friday (Mo=0, Mi=2, Fr=4 in Python)
- **Rest days:** Tuesday, Thursday, Saturday, Sunday
- "done" on training day or next day = counted as trained
- **Sarcasm trigger:** 2+ missed training days in last 14 days
- **Sarcasm lines:** 3 random witty responses from the butler 🎩

## Date Parsing

Recognizes German phrases:
- `heute` → today
- `gestern` → yesterday
- `vorgestern` → day before yesterday
- `DD.MM.YYYY` → explicit date

## Migration

`--init` safely migrates existing v1 databases to v2 without data loss:
- Adds new columns (`type`, `duration_min`, `calories`, `speed_kmh`, `weight_kg`)
- Creates `workout_status`, `workout_rules`, and `user_settings` tables
- Preserves all existing activity data
