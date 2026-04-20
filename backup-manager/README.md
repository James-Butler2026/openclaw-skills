# Backup Manager

Automatisches Backup-Tool für OpenClaw Workspace.

## Features

- Git-Backup mit automatischer Kategorisierung
- SQLite-DB Backup mit Zeitstempel und Rotation (7 Backups)
- Daemon-Modus für kontinuierliche Überwachung
- Status- und Log-Anzeige

## Backup-Skripte

| Script | Beschreibung |
|--------|--------------|
| `git_backup.py` | Haupt-Backup-Skript (Git + SQLite) |
| `backup_workspace.sh` | Shell-Wrapper |
| `git_auto_backup.sh` | Auto-Backup im Hintergrund |

## Verwendung

```bash
# Einmaliges Backup
python3 scripts/git_backup.py --once

# Daemon-Modus
python3 scripts/git_backup.py --daemon

# Status anzeigen
python3 scripts/git_backup.py --status
```
