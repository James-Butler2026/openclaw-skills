# Backup Manager Skill

Automatisches Git + SQLite Backup für OpenClaw Workspace.

## Features

- 🔄 **Git Auto-Commit** - Für Scripts und Konfigurationen
- 💾 **SQLite Backup** - Für Datenbanken
- 🕐 **Daemon-Modus** - Kontinuierliches Backup
- 🏷️ **Kategorisierung** - agents, scripts, skills, docs, memory

## Schnellstart

```bash
# Einmaliges Backup (Git + SQLite)
python3 scripts/git_auto_backup.py

# Nur SQLite-Backup
python3 scripts/git_auto_backup.py --sqlite-only

# Daemon-Modus (kontinuierlich)
python3 scripts/git_auto_backup.py --daemon

# Mit Push zu Remote
python3 scripts/git_auto_backup.py --push

# Status anzeigen
python3 scripts/git_auto_backup.py --status
```

## Backup-Struktur

```
~/.openclaw/workspace/
├── scripts/          → Committed zu Git
├── skills/           → Committed zu Git
├── *.md             → Committed zu Git
├── data/*.db         → SQLite Backup
└── logs/backup.log   → Backup-Log
```

## Cron-Job

```bash
# Alle 6 Stunden Backup
0 */6 * * * cd ~/.openclaw/workspace && python3 scripts/git_auto_backup.py
```

## Log-Datei

- Pfad: `logs/backup.log`
- Enthält: Zeitstempel, Backup-Typ, Erfolg/Fehler

## Was wird gesichert

- ✅ `scripts/` - Alle Python-Scripts
- ✅ `skills/` - Skill-Dokumentationen
- ✅ `*.md` - Konfigurationen
- ✅ `data/*.db` - SQLite Datenbanken
- ❌ `venv/` - Virtual Environment
- ❌ `__pycache__/` - Python-Cache
- ❌ `.env` - Credentials (exkludiert in .gitignore)

---

*Teil der OpenClaw Skills Collection* 🎩
