#!/bin/bash
# MusicGen Installer v2 - Saubere Installation ohne audiocraft (nur transformers)
set -e
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$SKILL_DIR/venv"
SCRIPT="$SKILL_DIR/scripts/generate.py"
LOCK="$SKILL_DIR/.installed"

install() {
    echo "🎵 Installiere MusicGen via Transformers (CPU, ~5-10 Min)..."
    
    if [ -f "$LOCK" ]; then
        echo "   Bereits installiert."
        return
    fi
    
    # Alte venv komplett löschen + frisch machen
    rm -rf "$VENV"
    python3 -m venv "$VENV"
    source "$VENV/bin/activate"
    
    pip install --quiet --upgrade pip setuptools wheel 2>&1 | tail -1
    
    # Nur das Nötigste: aktuelle torch + transformers + torchaudio
    pip install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu 2>&1 | tail -1
    pip install --quiet transformers accelerate 2>&1 | tail -1
    
    touch "$LOCK"
    echo ""
    echo "✅ MusicGen installiert!"
    echo "   Nutzung: python3 $SCRIPT --prompt \"rock song\" --output /pfad/zu/song.wav --duration 8"
}

uninstall() {
    echo "🗑️ Entferne MusicGen..."
    rm -f "$LOCK"
    # Komplette Skill-Directory löschen
    echo "   Skills-Ordner: rm -rf $SKILL_DIR"
    echo "   HF-Cache: ~/.cache/huggingface/hub/models--facebook--musicgen*"
    echo "✅ MusicGen entfernt."
    echo "   Mit 'rm -rf $SKILL_DIR' komplett weg."
}

case "${1:-install}" in
    install) install ;;
    uninstall) uninstall ;;
    *) echo "Usage: $0 {install|uninstall}" ;;
esac
