#!/usr/bin/env python3
"""
Piper TTS - Deutsche Text-to-Speech mit Thorsten-Stimme
Lokale Sprachsynthese, keine API-Keys, keine Kosten
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Piper Konfiguration
PIPER_BINARY = "/home/node/.local/bin/piper"  # Neues frisch gebautes Binary
PIPER_MODEL = "/usr/local/share/piper-voices/de_DE-thorsten-medium.onnx"
DEFAULT_OUTPUT = "/tmp/piper_output.wav"

# Umgebungsvariablen für Piper
os.environ['LD_LIBRARY_PATH'] = '/tmp/piper-build/build/pi/lib:/usr/lib/x86_64-linux-gnu'
os.environ['ESPEAK_DATA_PATH'] = '/tmp/piper-build/build/pi/share/espeak-ng-data'


def check_piper():
    """Prüft ob Piper installiert ist"""
    if not Path(PIPER_BINARY).exists():
        raise RuntimeError(
            f"Piper nicht gefunden unter {PIPER_BINARY}\n"
            "Installieren mit: pip install piper-tts"
        )
    
    if not Path(PIPER_MODEL).exists():
        raise RuntimeError(
            f"Thorsten-Modell nicht gefunden unter {PIPER_MODEL}\n"
            "Modell herunterladen: ..."
        )


def generate_speech(text, output_path=DEFAULT_OUTPUT, speed=1.0, play=False, send_voice=False):
    """
    Generiert Sprache aus Text
    
    Args:
        text: Zu sprechender Text
        output_path: Ausgabedatei (WAV)
        speed: Sprechgeschwindigkeit (0.5-2.0)
        play: Nach Generierung abspielen
        send_voice: Als Telegram-Voice senden
    
    Returns:
        Pfad zur WAV-Datei
    """
    check_piper()
    
    print(f"🎙️ Generiere Sprache...")
    print(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"   Stimme: Thorsten (deutsch)")
    print(f"   Geschwindigkeit: {speed}x")
    
    # Piper direkt ausführen mit korrekten Umgebungsvariablen
    import os
    
    # Setze Umgebungsvariablen für Piper
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = '/home/node/.local/lib/piper:/usr/lib/x86_64-linux-gnu'
    env['ESPEAK_DATA_PATH'] = '/tmp/piper-build/build/pi/share/espeak-ng-data'
    
    # Piper Binary
    piper_bin = '/home/node/.local/bin/piper'
    
    # Befehl zusammenbauen
    cmd = [
        piper_bin,
        "--model", PIPER_MODEL,
        "--output_file", output_path,
        "--length_scale", str(1.0 / speed)
    ]
    
    # Piper ausführen
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env  # Wichtig: Umgebungsvariablen übergeben!
        )
        
        stdout, stderr = process.communicate(input=text)
        
        if process.returncode != 0:
            raise RuntimeError(f"Piper Fehler: {stderr}")
        
        file_size = Path(output_path).stat().st_size / 1024
        print(f"✅ Audio generiert: {output_path}")
        print(f"   Größe: {file_size:.1f} KB")
        
    except Exception as e:
        raise RuntimeError(f"Fehler bei Piper: {e}")
    
    # Abspielen wenn gewünscht
    if play:
        play_audio(output_path)
    
    # Als Voice senden wenn gewünscht
    if send_voice:
        send_voice_message(output_path)
    
    return output_path


def play_audio(audio_path):
    """Spielt Audio-Datei ab"""
    print(f"🔊 Spiele ab...")
    
    # Versuche verschiedene Player
    players = [
        ["aplay", audio_path],           # ALSA
        ["paplay", audio_path],          # PulseAudio
        ["ffplay", "-nodisp", "-autoexit", audio_path],  # FFmpeg
        ["mpg123", audio_path],          # MPEG Player
    ]
    
    for player in players:
        try:
            result = subprocess.run(
                player,
                capture_output=True,
                timeout=30,
                check=False
            )
            if result.returncode == 0:
                print(f"   ✅ Abspielen beendet")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print(f"   ⚠️ Kein Audio-Player gefunden. Datei: {audio_path}")


def send_voice_message(audio_path):
    """Sendet Audio als Telegram Voice Message"""
    print(f"📱 Sende als Voice-Message...")
    
    # Versuche Telegram via OpenClaw
    try:
        # Prüfe ob message Tool verfügbar ist
        # Da wir in der Sub-Agent Umgebung sind, versuchen wir es
        cmd = [
            "python3", "-c",
            f"""
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace')
try:
    from scripts.send_voice import send_voice_message
    send_voice_message('{audio_path}', 'Erhaltene Sprachnachricht')
    print('✅ Voice-Message gesendet!')
except Exception as e:
    print(f'⚠️ Senden fehlgeschlagen: {{e}}')
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(result.stdout)
        if result.returncode != 0:
            print(f"   ⚠️ Hinweis: {result.stderr}")
            
    except Exception as e:
        print(f"   ⚠️ Senden nicht möglich: {e}")
        print(f"   Audio-Datei verfügbar unter: {audio_path}")


def read_text_from_file(file_path):
    """Liest Text aus Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Konnte Datei nicht lesen: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Piper TTS - Deutsche Text-to-Speech mit Thorsten',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s "Hallo Welt"
  %(prog)s "Guten Morgen" --play
  %(prog)s "Erinnerung" --send
  %(prog)s -f nachricht.txt -o custom.wav --play
        """
    )
    
    parser.add_argument('text', nargs='?', help='Text zu sprechen')
    parser.add_argument('--file', '-f', help='Text aus Datei laden')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT, help='Ausgabedatei')
    parser.add_argument('--speed', type=float, default=1.0, help='Sprechgeschwindigkeit')
    parser.add_argument('--play', '-p', action='store_true', help='Direkt abspielen')
    parser.add_argument('--send', '-s', action='store_true', help='Als Voice senden')
    
    args = parser.parse_args()
    
    # Text holen (Parameter oder Datei)
    if args.file:
        text = read_text_from_file(args.file)
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)
    
    # Validierung
    if not text.strip():
        print("❌ Fehler: Leerer Text!")
        sys.exit(1)
    
    if args.speed < 0.5 or args.speed > 2.0:
        print("⚠️ Warnung: Speed außerhalb normaler Range (0.5-2.0)")
    
    # Generieren
    try:
        result = generate_speech(
            text=text,
            output_path=args.output,
            speed=args.speed,
            play=args.play,
            send_voice=args.send
        )
        
        print(f"\n🎉 Fertig! {result}")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
