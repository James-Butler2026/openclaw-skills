# Sports Tracker with Komoot Integration

Track your workouts (P90X, cycling, hiking, running) with SQLite, CLI tools, automatic calorie calculation, and **automatic tour import from Komoot**.

## Features

- **Manual Logging** - P90X, cycling, hiking, running via CLI
- **Automated Komoot Import** - Fetches tours every 4 hours, with dedup
- **Auto-Calorie Calculation** - Based on MET formula and body weight
- **Workout Tracking** - Training day management (Mon/Wed/Fri)
- **GPX Export** - Download GPX data from Komoot tours
- **Multi-format Reports** - Weekly, monthly, full-month, detailed stats

## Categories

| Activity  | Type        | Emoji |
|-----------|-------------|-------|
| P90X      | Strength    | 💪    |
| Cycling   | Cardio      | 🚴    |
| Hiking    | Cardio      | 🥾    |
| Running   | Cardio      | 🏃    |

> Walking and nordic walking are classified under Hiking.

## Quick Start

```bash
# Manual activity logging
python3 skills/sports-tracker/scripts/sports_tracker.py --add "5 km Hiking"

# Mark P90X as done
python3 skills/sports-tracker/scripts/sports_tracker.py --done

# Weekly report
python3 skills/sports-tracker/scripts/sports_tracker.py --week

# Import Komoot tours
python3 skills/sports-tracker/scripts/komoot_import.py

# With GPX download
python3 skills/sports-tracker/scripts/komoot_import.py --export-gpx
```

## Komoot Sport-Type Mapping

| Komoot Type                          | Sport Tracker |
|--------------------------------------|---------------|
| touring_cycling, cycling, mtb        | Cycling       |
| hiking, hike                         | Hiking        |
| walking, walk, nordic_walking        | Hiking        |
| running, run, trail_running          | Running       |
| skiing, ski_touring, snowboard       | Skiing        |

## Calorie Calculation

Formula: `Kcal = MET × weight_kg × duration_hours`

| Activity | MET | Duration Calculation |
|----------|-----|---------------------|
| Cycling  | 8.0 | km / 18 km/h        |
| Hiking   | 3.5 | km / 4.5 km/h       |
| P90X     | 6.0 | 60 min (default)    |

**Default weight:** 120 kg (configurable with `--weight`)

## Automated Scheduling

- **Every 4 hours** - Komoot sync via cron
- **Mon/Wed/Fri 21:00** - Workout reminder
- **On change only** - No spam on unchanged status

## Database

Local SQLite database at `data/sports_tracker.db`. Offline-first, private, portable.

### Setup

1. Add Komoot credentials to `.env`:
   ```
   KOMOOT_EMAIL=your@email.com
   KOMOOT_PASSWORD=your_password
   KOMOOT_USER_ID=your_user_id
   ```

2. Initialize the database:
   ```bash
   python3 skills/sports-tracker/scripts/sports_tracker.py --init
   ```

3. Test Komoot import:
   ```bash
   python3 skills/sports-tracker/scripts/komoot_import.py
   ```

## License

MIT
