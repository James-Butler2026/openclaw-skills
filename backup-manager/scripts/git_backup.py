#!/usr/bin/env python3
"""
Git Backup Manager - Kombiniertes Backup-Tool
Features:
- Einmaliges Backup (--once)
- Daemon-Modus (--daemon) für automatische Überwachung
- SQLite DB Backup (--db-backup)
- Status-Anzeige (--status)
- Log-Anzeige (--log)
- Automatische Kategorisierung der Änderungen
- Push zu Remote (--push)

Ersetzt: backup_tool.py + git_auto_backup.py
"""

import os
import sys
import time
import subprocess
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# Zentrales Logging importieren
sys.path.insert(0, '/home/node/.openclaw/workspace/scripts')
from logger_config import get_logger

logger = get_logger(__name__)

WORKSPACE = Path("/home/node/.openclaw/workspace")
DB_PATH = WORKSPACE / "data" / "james.db"
DB_BACKUP_DIR = WORKSPACE / "backup" / "db"
LAST_CHECK_FILE = Path("/tmp/git_backup_last_check")
LOG_FILE = Path("/tmp/workspace_backup.log")
LOCK_FILE = Path("/tmp/workspace_backup.lock")


def run_git_command(args, cwd=WORKSPACE):
    """Führt Git-Befehl aus"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Git-Befehl fehlgeschlagen: {e}")
        return False, "", str(e)


def backup_sqlite_db(keep_backups: int = 7) -> bool:
    """
    Erstellt ein SQLite-Backup mit Zeitstempel.
    Löscht alte Backups, behält nur die letzten N Backups.
    
    Args:
        keep_backups: Anzahl der zu behaltenden Backups (Standard: 7)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    if not DB_PATH.exists():
        logger.warning(f"SQLite-DB nicht gefunden: {DB_PATH}")
        return False
    
    try:
        # Backup-Verzeichnis erstellen
        DB_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Zeitstempel für Backup-Datei
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = DB_BACKUP_DIR / f"james_backup_{timestamp}.db"
        
        # SQLite-Backup erstellen (Kopie)
        shutil.copy2(DB_PATH, backup_file)
        
        # Alte Backups aufzählen und sortieren
        backups = sorted(DB_BACKUP_DIR.glob("james_backup_*.db"), key=lambda x: x.stat().st_mtime)
        
        # Überschüssige Backups löschen
        if len(backups) > keep_backups:
            for old_backup in backups[:-keep_backups]:
                old_backup.unlink()
                logger.debug(f"Altes DB-Backup gelöscht: {old_backup.name}")
        
        logger.info(f"SQLite-Backup erstellt: {backup_file.name} ({len(backups)} Backups)")
        
        # Ins Log schreiben
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💾 SQLite-Backup: {backup_file.name}\n")
        
        return True
        
    except Exception as e:
        logger.exception("SQLite-Backup fehlgeschlagen")
        return False


def has_changes():
    """Prüft ob es Änderungen gibt"""
    success, stdout, _ = run_git_command(['status', '--porcelain'])
    if not success:
        return False
    return bool(stdout.strip())


def get_changed_files():
    """Holt geänderte Dateien mit Status"""
    success, stdout, _ = run_git_command(['status', '--porcelain'])
    if not success:
        return []
    
    files = []
    for line in stdout.strip().split('\n'):
        if line:
            status = line[:2].strip()
            filename = line[3:].strip().strip('"')
            files.append(f"{status}:{filename}")
    return files


def categorize_changes(files):
    """Kategorisiert geänderte Dateien"""
    categories = set()
    for f in files:
        fname = f.split(':', 1)[1] if ':' in f else f
        if 'scripts/agents/' in fname:
            categories.add('agents')
        elif 'scripts/' in fname:
            categories.add('scripts')
        elif 'skills/' in fname:
            categories.add('skills')
        elif 'docs/' in fname:
            categories.add('docs')
        elif 'memory/' in fname:
            categories.add('memory')
        elif 'cron-jobs/' in fname:
            categories.add('cron')
        elif '.md' in fname:
            categories.add('config')
        elif '.env' in fname:
            categories.add('secrets')
    return sorted(list(categories))


def backup_changes(push=False, force=False):
    """Führt Backup durch"""
    # Verhindere parallele Ausführung
    if LOCK_FILE.exists() and not force:
        logger.info("Backup läuft bereits...")
        return False
    
    try:
        LOCK_FILE.touch()
        
        if not has_changes():
            logger.debug("Keine Änderungen zum Committen")
            return True
        
        changed_files = get_changed_files()
        categories = categorize_changes(changed_files)
        
        # Stagen
        success, _, stderr = run_git_command(['add', '-A'])
        if not success:
            logger.error(f"Git add fehlgeschlagen: {stderr}")
            return False
        
        # Commit-Message generieren
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        cat_str = ', '.join(categories) if categories else 'files'
        
        commit_msg = f"Auto-backup: {cat_str} ({len(changed_files)} changes) [{timestamp}]"
        
        # Commit
        success, stdout, stderr = run_git_command(['commit', '-m', commit_msg])
        
        if not success:
            logger.error(f"Git commit fehlgeschlagen: {stderr}")
            return False
        
        # Hash holen
        _, hash_out, _ = run_git_command(['rev-parse', '--short', 'HEAD'])
        commit_hash = hash_out.strip() if hash_out else 'unknown'
        
        logger.info(f"Committed: {commit_hash} - {len(changed_files)} Dateien ({cat_str})")
        
        # Optional: Push
        if push:
            success, _, stderr = run_git_command(['push', 'origin', 'master'])
            if success:
                logger.info("Zu Remote gepusht")
            else:
                logger.warning(f"Push fehlgeschlagen: {stderr}")
        
        # Ins Log schreiben
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {commit_hash}: {len(changed_files)} files ({cat_str})\n")
        
        return True
        
    except Exception as e:
        logger.exception("Backup fehlgeschlagen")
        return False
        
    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()


def show_status():
    """Zeigt Git-Status"""
    print("📊 Git Status:")
    print("=" * 50)
    
    success, stdout, stderr = run_git_command(['status'])
    if success:
        print(stdout)
    else:
        print(f"❌ Fehler: {stderr}")
    
    print("\n📈 Letzte Commits:")
    print("=" * 50)
    success, stdout, _ = run_git_command(['log', '--oneline', '-5'])
    if success:
        print(stdout)


def show_log(lines=20):
    """Zeigt Backup-Log"""
    if LOG_FILE.exists():
        print(f"📜 Backup-Log ({LOG_FILE}):")
        print("=" * 50)
        content = LOG_FILE.read_text()
        lines_content = content.split('\n')
        print('\n'.join(lines_content[-lines:] if len(lines_content) > lines else lines_content))
    else:
        print("ℹ️ Kein Log vorhanden")


def daemon_mode():
    """Daemon-Modus für automatische Überwachung"""
    print("🔄 Git Backup Daemon gestartet")
    print(f"📁 Überwache: {WORKSPACE}")
    print("⏱️  Prüfe alle 60 Sekunden auf Änderungen...")
    print("🛑 Beenden mit Ctrl+C\n")
    
    while True:
        try:
            if has_changes():
                logger.info("Änderungen erkannt, starte Backup...")
                backup_changes()
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n👋 Daemon beendet")
            break
        except Exception as e:
            logger.exception("Fehler im Daemon")
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(
        description='Git Backup Manager - Automatische Workspace-Backups'
    )
    
    parser.add_argument('--daemon', '-d', action='store_true', 
                        help='Als Daemon laufen (überwacht kontinuierlich)')
    parser.add_argument('--once', '-o', action='store_true', 
                        help='Einmaliges Backup durchführen')
    parser.add_argument('--db-backup', '-b', action='store_true', 
                        help='Nur SQLite-DB backup durchführen')
    parser.add_argument('--status', '-s', action='store_true', 
                        help='Git-Status anzeigen')
    parser.add_argument('--log', '-l', action='store_true', 
                        help='Backup-Log anzeigen')
    parser.add_argument('--push', '-p', action='store_true', 
                        help='Mit Push zu Remote')
    parser.add_argument('--force', '-f', action='store_true', 
                        help='Force (ignoriere Lock)')
    parser.add_argument('--lines', type=int, default=20, 
                        help='Anzahl der Log-Zeilen (Standard: 20)')
    parser.add_argument('--keep-db', type=int, default=7, 
                        help='Anzahl der DB-Backups (Standard: 7)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Ausführliche Logging-Ausgabe')
    
    args = parser.parse_args()
    
    # Logging-Level anpassen
    if args.verbose:
        logger.setLevel('DEBUG')
    
    if args.status:
        show_status()
    elif args.log:
        show_log(args.lines)
    elif args.db_backup:
        success = backup_sqlite_db(keep_backups=args.keep_db)
        sys.exit(0 if success else 1)
    elif args.daemon:
        daemon_mode()
    elif args.once:
        # Git-Backup + SQLite-Backup
        git_success = backup_changes(push=args.push, force=args.force)
        db_success = backup_sqlite_db(keep_backups=args.keep_db)
        sys.exit(0 if (git_success and db_success) else 1)
    else:
        # Standard: Git-Backup + SQLite-Backup
        git_success = backup_changes(push=args.push, force=args.force)
        db_success = backup_sqlite_db(keep_backups=args.keep_db)
        sys.exit(0 if (git_success and db_success) else 1)


if __name__ == '__main__':
    main()
