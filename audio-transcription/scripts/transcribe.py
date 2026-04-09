#!/usr/bin/env python3
"""
Transkription-Script für Sprachnachrichten via faster-whisper
Nutzt das venv in /home/node/.openclaw/venv
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# Venv-Pfade
VENV_PATH = Path("/home/node/.openclaw/venv")
WHISPER_BIN = VENV_PATH / "bin" / "whisper-ctranslate2"
PYTHON_BIN = VENV_PATH / "bin" / "python3"

def check_venv():
    """Prüft ob das venv existiert"""
    if not VENV_PATH.exists():
        print(f"❌ Venv nicht gefunden: {VENV_PATH}", file=sys.stderr)
        print("Bitte faster-whisper zuerst installieren:", file=sys.stderr)
        print("  python3 -m venv /home/node/.openclaw/venv", file=sys.stderr)
        print("  /home/node/.openclaw/venv/bin/pip install faster-whisper", file=sys.stderr)
        sys.exit(1)

def transcribe_file(audio_path: str, language: str = "auto", model: str = "base") -> str:
    """
    Transkribiert eine Audiodatei mit faster-whisper
    
    Args:
        audio_path: Pfad zur Audio-Datei
        language: Sprachcode (z.B. 'de', 'en') oder 'auto' für Auto-Erkennung
        model: Modell-Name (tiny, base, small, medium, large-v3)
    
    Returns:
        Der transkribierte Text
    """
    check_venv()
    
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio-Datei nicht gefunden: {audio_path}")
    
    try:
        cmd = [
            str(WHISPER_BIN),
            str(audio_file),
            "--model", model,
            "--output_format", "txt",
            "--output_dir", "/tmp",
        ]
        
        if language != "auto":
            cmd.extend(["--language", language])
        
        print(f"🎙️  Transkribiere: {audio_file.name}")
        print(f"   Modell: {model}, Sprache: {language}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/tmp"
        )
        
        if result.returncode != 0:
            print(f"❌ Fehler bei der Transkription:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)
        
        output_file = Path(f"/tmp/{audio_file.stem}.txt")
        if output_file.exists():
            text = output_file.read_text(encoding="utf-8").strip()
            output_file.unlink()
            return text
        else:
            return result.stdout.strip()
            
    except Exception as e:
        raise RuntimeError(f"Transkription fehlgeschlagen: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Transkribiert Audio-Dateien mit faster-whisper"
    )
    parser.add_argument(
        "audio_file",
        help="Pfad zur Audio-Datei (mp3, ogg, wav, etc.)"
    )
    parser.add_argument(
        "--language", "-l",
        default="auto",
        help="Sprache der Aufnahme (z.B. 'de', 'en'). Default: auto-erkennen"
    )
    parser.add_argument(
        "--model", "-m",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper-Modell (tiny=fast, large-v3=beste Qualität). Default: small"
    )
    
    args = parser.parse_args()
    
    try:
        text = transcribe_file(args.audio_file, args.language, args.model)
        print("\n📝 Transkription:")
        print("-" * 40)
        print(text)
        print("-" * 40)
    except Exception as e:
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
