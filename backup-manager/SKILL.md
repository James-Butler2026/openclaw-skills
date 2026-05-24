# Git Backup Manager

Kombiniertes Backup-Tool für den Workspace. Ersetzt `backup_tool.py` und `git_auto_backup.py`.

## Features

- ✅ **Git-Backup** mit automatischer Kategorisierung
- 💾 **SQLite-DB Backup** mit Zeitstempel und Rotation (7 Backups)
- 🔄 **Daemon-Modus** für kontinuierliche Überwachung
- 📊 **Status- und Log-Anzeige**
- 🚀 **Optionaler Push zu Remote**

## Kategorisierung

Automatische Erkennung von Änderungen:
- `agents/` → **agents**
- `scripts/` → **scripts**
- `skills/` → **skills**
- `docs/` → **docs**
- `memory/` → **memory**
- `cron-jobs/` → **cron**
- `.md` → **config**
- `.env` → **secrets**

## Verwendung

### Einmaliges Backup (Git + SQLite)
```bash
python3 scripts/git_backup.py --once
```

### Nur SQLite-Backup
```bash
python3 scripts/git_backup.py --db-backup
```

### Daemon-Modus (kontinuierlich)
```bash
python3 scripts/git_backup.py --daemon
```

### Mit Push zu Remote
```bash
python3 scripts/git_backup.py --once --push
```

### Status anzeigen
```bash
python3 scripts/git_backup.py --status
```

### Log anzeigen
```bash
python3 scripts/git_backup.py --log
python3 scripts/git_backup.py --log --lines 50
```

## Cron-Job

Automatisches tägliches Backup um **03:00 Uhr**:
- Git-Commit aller Änderungen
- SQLite-DB Backup mit Zeitstempel
- Automatische Löschung alter Backups (behält 7)

## Backup-Struktur

```
backup/
├── removed_scripts_YYYYMMDD/     # Entfernte Scripts (Sicherung)
└── db/
    ├── james_backup_20250325_120000.db
    ├── james_backup_20250325_130000.db
    └── ... (max. 7 Backups)
```

## Log-Datei

`/tmp/workspace_backup.log`

## Entfernte alte Scripts

| Script | Grund |
|--------|-------|
| `backup_tool.py` | Veraltet, durch git_backup.py ersetzt |
| `git_auto_backup.py` | Veraltet, durch git_backup.py ersetzt |
| `test_mammouth_models.py` | Nur Test, nicht produktiv |
| `transcribe.py` | Duplikat (existiert in Skill) |

Alle entfernten Scripts sind im `backup/removed_scripts_20250325/` Verzeichnis sicher aufbewahrt.
