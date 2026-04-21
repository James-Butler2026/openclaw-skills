#!/usr/bin/env python3
"""
ElevenLabs TTS Script - Deutsche Sprachausgabe
Test- und Produktions-Script für Text-to-Speech
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Default-Config
DEFAULT_MODEL = "eleven_multilingual_v2"  # Beste Qualität für 70+ Sprachen inkl. Deutsch
DEFAULT_VOICE = "NkhHdPbLqYzmdIaSUuIy"  # Drachenlord geklonte Stimme
DEFAULT_OUTPUT = "/tmp/elevenlabs_output.mp3"

# Statistik-Datei für kumulierte Zeichen (im Skill-Data-Verzeichnis)
STATS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'elevenlabs_stats.json')
# ElevenLabs: 37,472 Credits = 10€ -> 1 Credit ≈ 0.000267€ -> 1000 Zeichen ≈ 0.27€
COST_PER_1000_CHARS = 0.267  # 1000 Zeichen = 0,267€ (basierend auf 10€ = 37,472 Credits)


def load_api_key():
    """API Key aus .env laden"""
    env_paths = [
        Path(__file__).parent.parent / ".env",
        Path("/home/node/.openclaw/workspace/.env"),
        Path(".env")
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ELEVENLABS_API_KEY='):
                        return line.split('=', 1)[1].strip().strip('"').strip("'")
    
    return os.getenv('ELEVENLABS_API_KEY')


def load_stats():
    """Lädt kumulierte Statistik"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"total_chars": 0, "total_cost_eur": 0.0}


def save_stats(stats):
    """Speichert kumulierte Statistik"""
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)


def list_voices(api_key):
    """Alle verfügbaren Stimmen abrufen"""
    url = "https://api.elevenlabs.io/v1/voices"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get('voices', [])
    except urllib.error.HTTPError as e:
        print(f"❌ Fehler: {e.code} - {e.reason}")
        if e.code == 401:
            print("   Ungültiger API Key!")
        return []
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return []


def list_models(api_key):
    """Alle verfügbaren Modelle abrufen"""
    url = "https://api.elevenlabs.io/v1/models"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return {}


def generate_speech(api_key, text, voice_id=None, model=None, output_path=None, voice_settings=None):
    """Text zu Sprache umwandeln"""
    
    voice_id = voice_id or DEFAULT_VOICE
    model = model or DEFAULT_MODEL
    output_path = output_path or DEFAULT_OUTPUT
    
    # Drachenlord Voice Settings - Konstantin's Settings
    # SPEED: 1.0 = normal, 1.2 = schnell, 0.7 = langsam
    # User request 18.04.2026: speed 0.8 für bessere Verständlichkeit
    if voice_settings is None:
        voice_settings = {
            "stability": 1.0,              # Maximum! Konsistente Stimme
            "similarity_boost": 0.9,       # Hohe Ähnlichkeit
            "style": 0.1,                # Wenig Stil-Variation
            "use_speaker_boost": True,     # Klarere Aussprache
            "speed": 0.8                   # Etwas flotter - User-Request 18.04.2026
        }
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": voice_settings
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
        "xi-api-key": api_key
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio_data = resp.read()
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return output_path
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ API Fehler: {e.code} - {e.reason}")
        print(f"   Details: {error_body}")
        return None
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None


def filter_german_voices(voices):
    """Deutsche Stimmen herausfiltern"""
    german = []
    
    for voice in voices:
        name = voice.get('name', '').lower()
        desc = voice.get('description', '').lower()
        labels = voice.get('labels', {})
        
        # Prüfe auf deutsche Indikatoren
        is_german = (
            'german' in name or 
            'german' in desc or
            'deutsch' in name or
            'deutsch' in desc or
            labels.get('language') == 'de' or
            labels.get('accent') == 'german'
        )
        
        if is_german:
            german.append(voice)
    
    return german


def main():
    """Hauptfunktion"""
    api_key = load_api_key()
    
    if not api_key:
        print("❌ Kein API Key gefunden!")
        print("   Bitte in .env eintragen: ELEVENLABS_API_KEY=sk_...")
        sys.exit(1)
    
    # Kurz-Check: Gültiger Key?
    print("🔑 API Key gefunden... teste...")
    
    # Parse Kommandozeilenargumente
    if len(sys.argv) < 2:
        print("""
ElevenLabs TTS Script

Nutzung:
  python3 elevenlabs_tts.py list              # Alle Stimmen auflisten
  python3 elevenlabs_tts.py list-de           # Nur deutsche Stimmen
  python3 elevenlabs_tts.py models            # Alle Modelle auflisten  
  python3 elevenlabs_tts.py speak "Text"      # Text als Sprache (Standard-Stimme)
  python3 elevenlabs_tts.py speak "Text" --voice VOICE_ID
  python3 elevenlabs_tts.py speak "Text" --model MODEL_ID

Beispiele:
  python3 elevenlabs_tts.py speak "Hallo Welt"
  python3 elevenlabs_tts.py speak "Guten Morgen" --voice brian
  python3 elevenlabs_tts.py speak "Test" --model eleven_flash_v2.5
""")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "list":
        print("📋 Lade alle Stimmen...")
        voices = list_voices(api_key)
        
        print(f"\n🎙️  {len(voices)} Stimmen gefunden:\n")
        for voice in voices:
            vid = voice.get('voice_id', 'N/A')
            name = voice.get('name', 'Unbekannt')
            category = voice.get('category', 'N/A')
            desc = voice.get('description', 'Keine Beschreibung')[:50]
            
            print(f"  {vid:<24} | {name:<20} | {category:<10} | {desc}...")
        
    elif command == "list-de":
        print("🇩🇪 Suche deutsche Stimmen...")
        voices = list_voices(api_key)
        german = filter_german_voices(voices)
        
        if german:
            print(f"\n🎙️  {len(german)} deutsche Stimmen:\n")
            for voice in german:
                vid = voice.get('voice_id', 'N/A')
                name = voice.get('name', 'Unbekannt')
                labels = voice.get('labels', {})
                lang = labels.get('language', 'N/A')
                print(f"  ID: {vid}")
                print(f"     Name: {name}")
                print(f"     Sprache: {lang}")
                print()
        else:
            print("⚠️  Keine deutschen Stimmen gefunden.")
            print("   Versuchen Sie 'list' und suchen Sie nach 'German' oder 'Deutsch' im Namen.")
    
    elif command == "models":
        print("🔧 Lade verfügbare Modelle...")
        models = list_models(api_key)
        
        if isinstance(models, dict) and 'models' in models:
            print(f"\n🔧 {len(models['models'])} Modelle:\n")
            for model in models['models']:
                mid = model.get('model_id', 'N/A')
                name = model.get('name', 'Unbekannt')
                desc = model.get('description', '')[:60]
                print(f"  {mid:<30} | {name:<25} | {desc}...")
        else:
            print("   Antwort:", json.dumps(models, indent=2)[:500])
    
    elif command == "speak":
        if len(sys.argv) < 3:
            print("❌ Text fehlt! Beispiel: python3 elevenlabs_tts.py speak 'Hallo'")
            sys.exit(1)
        
        text = sys.argv[2]
        voice = None
        model = None
        
        # Parse optional args
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--voice" and i + 1 < len(sys.argv):
                voice = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--model" and i + 1 < len(sys.argv):
                model = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        voice = voice or DEFAULT_VOICE
        model = model or DEFAULT_MODEL
        
        print(f"🎙️  Generiere Sprache...")
        print(f"   Text: '{text[:50]}...'" if len(text) > 50 else f"   Text: '{text}'")
        print(f"   Stimme: {voice}")
        print(f"   Modell: {model}")
        
        result = generate_speech(api_key, text, voice, model)
        
        if result:
            # Statistik für NEW RULE (17.04.2026) - Kumuliert
            char_count = len(text)
            # Geschätzte Dauer: ca. 13-15 chars pro Sekunde bei speed 0.8
            estimated_duration = char_count / 15
            
            # Kumulierte Statistik laden und aktualisieren
            stats = load_stats()
            stats["total_chars"] += char_count
            stats["total_cost_eur"] = stats["total_chars"] / 1000 * COST_PER_1000_CHARS
            save_stats(stats)
            
            print(f"✅ Gespeichert: {result}")
            print(f"   Abspielen: mpv {result}  oder  aplay {result}")
            
            # Statistik-Zeile (NEW RULE 17.04.2026)
            stats_line = f"[{char_count} Zeichen | Total: {stats['total_chars']} | {stats['total_cost_eur']:.2f}€ | {estimated_duration:.1f}s]"
            print(stats_line)
            
            # Maschinenlesbarer Output für Integration
            print(f"STATS:{char_count}:{stats['total_chars']}:{stats['total_cost_eur']:.2f}:{estimated_duration:.1f}")
        else:
            print("❌ Fehler bei der Generierung")
            sys.exit(1)
    
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print("   Nutzen Sie ohne Argumente für Hilfe")


if __name__ == "__main__":
    main()
