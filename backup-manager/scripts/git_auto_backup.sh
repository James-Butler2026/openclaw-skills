#!/bin/bash
# Git Auto-Backup Script - NUR Skills und Scripts
# Committet automatisch bei Änderungen

REPO_DIR="/home/node/.openclaw/workspace"
cd "$REPO_DIR" || exit 1

# Prüfe auf Änderungen in skills/ und scripts/
git add skills/ scripts/ .gitignore 2>/dev/null

# Prüfe ob es Änderungen gibt
if git diff --cached --quiet; then
    echo "Keine Änderungen in skills/ oder scripts/"
    exit 0
fi

# Änderungen vorhanden - committe
CHANGES=$(git diff --cached --name-only | wc -l)
echo "$CHANGES Dateien geändert - erstelle Backup..."

# Commit mit Zeitstempel
git commit -m "Auto-backup: $(date '+%Y-%m-%d %H:%M') - $CHANGES changes"

echo "✅ Backup erstellt: $(date)"
