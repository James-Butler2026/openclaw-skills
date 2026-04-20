#!/bin/bash
# backup_workspace.sh - Automatisches Git-Backup für den Workspace
# Führt git add, commit und optional push durch

WORKSPACE_DIR="/home/node/.openclaw/workspace"
LOCK_FILE="/tmp/workspace_backup.lock"
LOG_FILE="/tmp/workspace_backup.log"

# Verhindere parallele Ausführung
if [ -f "$LOCK_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup läuft bereits" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
cd "$WORKSPACE_DIR" || exit 1

# Zeitstempel
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')

echo "[$TIMESTAMP] Backup gestartet..." >> "$LOG_FILE"

# Prüfe auf Änderungen
if git diff --quiet && git diff --cached --quiet; then
    echo "[$TIMESTAMP] Keine Änderungen zum Committen" >> "$LOG_FILE"
    rm "$LOCK_FILE"
    exit 0
fi

# Status ins Log
echo "[$TIMESTAMP] Änderungen gefunden:" >> "$LOG_FILE"
git status --short >> "$LOG_FILE"

# Alle Änderungen stagen
git add -A

# Commit mit Zeitstempel
git commit -m "Auto-Backup: $DATE - Workspace Änderungen" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    COMMIT_HASH=$(git rev-parse --short HEAD)
    echo "[$TIMESTAMP] ✅ Commit erstellt: $COMMIT_HASH" >> "$LOG_FILE"
    
    # Optional: Push zu Remote (falls konfiguriert)
    # if git remote get-url origin >/dev/null 2>&1; then
    #     git push origin main >> "$LOG_FILE" 2>&1
    #     echo "[$TIMESTAMP] ✅ Zu Remote gepusht" >> "$LOG_FILE"
    # fi
else
    echo "[$TIMESTAMP] ❌ Commit fehlgeschlagen" >> "$LOG_FILE"
fi

rm "$LOCK_FILE"
echo "[$TIMESTAMP] Backup abgeschlossen" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
