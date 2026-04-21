#!/usr/bin/env python3
"""
ElevenLabs TTS Script - OPTIMIERTE VERSION v2.0
Deutsche Sprachausgabe mit Retry-Logik, Logging und Async-Support
"""

import os
import sys
import json
import logging
import urllib.request
import urllib.error
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/elevenlabs_tts.log')
    ]
)
logger = logging.getLogger(__name__)

# Konfiguration
@dataclass
class Config:
    """Konfigurationsdatenklasse"""
    default_voice: str = "NkhHdPbLqYzmdIaSUuIy"
    default_model: str = "eleven_multilingual_v2"
    default_output: str = "/tmp/elevenlabs_output.mp3"
    retry_attempts: int = 3
    retry_min_wait: int = 4
    retry_max_wait: int = 10
    api_timeout: int = 60
    cost_per_1000_chars: float = 0.267

def load_config() -> Config:
    """Lädt Konfiguration aus config.json oder verwendet Defaults"""
    config_file = Path(__file__).parent.parent / "config" / "config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                return Config(**data)
        except Exception as e:
            logger.warning(f"Konfiguration konnte nicht geladen werden: {e}")
    
    return Config()

CONFIG = load_config()

# Statistik
STATS_FILE = Path(__file__).parent.parent / "data" / "elevenlabs_stats.json"

def load_stats() -> Dict:
    """Lädt kumulierte Statistik"""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Statistik-Datei beschädigt, erstelle neue")
    return {"total_chars": 0, "total_cost_eur": 0.0}

def save_stats(stats: Dict) -> None:
    """Speichert kumulierte Statistik"""
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def update_stats(char_count: int) -> Dict:
    """Aktualisiert Statistik und gibt aktuelle Werte zurück"""
    stats = load_stats()
    stats["total_chars"] += char_count
    stats["total_cost_eur"] = stats["total_chars"] / 1000 * CONFIG.cost_per_1000_chars
    save_stats(stats)
    return stats

def load_api_key() -> Optional[str]:
    """API Key aus .env laden"""
    env_paths = [
        Path(__file__).parent.parent / ".env",
        Path("/home/node/.openclaw/workspace/.env"),
        Path(".env")
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('ELEVENLABS_API_KEY='):
                            return line.split('=', 1)[1].strip().strip('"').strip("'")
            except IOError as e:
                logger.error(f"Fehler beim Lesen von {env_path}: {e}")
    
    return os.getenv('ELEVENLABS_API_KEY')

@retry(
    stop=stop_after_attempt(CONFIG.retry_attempts),
    wait=wait_exponential(multiplier=1, min=CONFIG.retry_min_wait, max=CONFIG.retry_max_wait),
    retry=retry_if_exception_type((urllib.error.URLError, urllib.error.HTTPError))
)
def generate_speech(
    api_key: str,
    text: str,
    voice_id: Optional[str] = None,
    model: Optional[str] = None,
    output_path: Optional[str] = None,
    voice_settings: Optional[Dict] = None
) -> Optional[str]:
    """
    Text zu Sprache umwandeln (mit Retry)
    
    Args:
        api_key: ElevenLabs API Key
        text: Zu synthetisierender Text
        voice_id: Voice ID (default: Drachenlord)
        model: Modell-Name (default: eleven_multilingual_v2)
        output_path: Ausgabepfad (default: /tmp/elevenlabs_output.mp3)
        voice_settings: Zusätzliche Voice-Einstellungen
    
    Returns:
        Pfad zur generierten Audio-Datei oder None bei Fehler
    """
    voice_id = voice_id or CONFIG.default_voice
    model = model or CONFIG.default_model
    output_path = output_path or CONFIG.default_output
    
    # Voice Settings (optimiert für Drachenlord)
    if voice_settings is None:
        voice_settings = {
            "stability": 1.0,
            "similarity_boost": 0.9,
            "style": 0.1,
            "use_speaker_boost": True,
            "speed": 0.8
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
    
    logger.info(f"🎙️  Generiere Sprache: {len(text)} Zeichen")
    
    try:
        with urllib.request.urlopen(req, timeout=CONFIG.api_timeout) as resp:
            audio_data = resp.read()
            
            output_file = Path(output_path)
            output_file.write_bytes(audio_data)
            
            logger.info(f"✅ Audio gespeichert: {output_path}")
            return output_path
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if hasattr(e, 'read') else 'N/A'
        logger.error(f"❌ API Fehler: {e.code} - {e.reason}")
        logger.error(f"   Details: {error_body}")
        raise
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        raise

def list_voices(api_key: str) -> List[Dict]:
    """Liste alle verfügbaren Stimmen"""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"Accept": "application/json", "xi-api-key": api_key}
    
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get('voices', [])
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Stimmen: {e}")
        return []

def list_models(api_key: str) -> Dict:
    """Liste alle verfügbaren Modelle"""
    url = "https://api.elevenlabs.io/v1/models"
    headers = {"Accept": "application/json", "xi-api-key": api_key}
    
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Modelle: {e}")
        return {}

def print_stats(text: str, stats: Dict) -> str:
    """Generiert Statistik-Zeile"""
    char_count = len(text)
    estimated_duration = char_count / 15
    
    stats_line = f"[{char_count} Zeichen | Total: {stats['total_chars']} | {stats['total_cost_eur']:.2f}€ | {estimated_duration:.1f}s]"
    return stats_line

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ElevenLabs TTS - Deutsche Sprachausgabe',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s speak "Hallo Welt"
  %(prog)s speak "Text hier" --voice VOICE_ID --model MODEL
  %(prog)s list
  %(prog)s list-de
  %(prog)s models
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Befehl')
    
    # Speak Command
    speak_parser = subparsers.add_parser('speak', help='Text zu Sprache')
    speak_parser.add_argument('text', help='Zu synthetisierender Text')
    speak_parser.add_argument('--voice', default=CONFIG.default_voice, help='Voice ID')
    speak_parser.add_argument('--model', default=CONFIG.default_model, help='Modell')
    speak_parser.add_argument('--output', default=CONFIG.default_output, help='Ausgabepfad')
    
    # List Command
    list_parser = subparsers.add_parser('list', help='Alle Stimmen auflisten')
    
    # List-DE Command
    list_de_parser = subparsers.add_parser('list-de', help='Deutsche Stimmen auflisten')
    
    # Models Command
    models_parser = subparsers.add_parser('models', help='Alle Modelle auflisten')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # API Key laden
    api_key = load_api_key()
    if not api_key:
        logger.error("❌ Kein API Key gefunden! Bitte in .env eintragen: ELEVENLABS_API_KEY=sk_...")
        sys.exit(1)
    
    try:
        if args.command == 'speak':
            result = generate_speech(api_key, args.text, args.voice, args.model, args.output)
            
            if result:
                stats = update_stats(len(args.text))
                stats_line = print_stats(args.text, stats)
                
                print(f"✅ Gespeichert: {result}")
                print(f"   Abspielen: mpv {result}")
                print(stats_line)
                print(f"STATS:{len(args.text)}:{stats['total_chars']}:{stats['total_cost_eur']:.2f}:{len(args.text)/15:.1f}")
            else:
                logger.error("❌ Fehler bei der Generierung")
                sys.exit(1)
                
        elif args.command == 'list':
            voices = list_voices(api_key)
            print(f"\n🎙️  {len(voices)} Stimmen gefunden:\n")
            for voice in voices:
                print(f"  {voice.get('voice_id', 'N/A'):<24} | {voice.get('name', 'Unbekannt'):<20}")
                
        elif args.command == 'list-de':
            voices = list_voices(api_key)
            german = [v for v in voices if 'german' in v.get('name', '').lower() or 'deutsch' in v.get('name', '').lower()]
            print(f"\n🇩🇪 {len(german)} deutsche Stimmen:\n")
            for voice in german:
                print(f"  ID: {voice.get('voice_id')}")
                print(f"     Name: {voice.get('name')}")
                
        elif args.command == 'models':
            models = list_models(api_key)
            if 'models' in models:
                print(f"\n🔧 {len(models['models'])} Modelle:\n")
                for model in models['models']:
                    print(f"  {model.get('model_id', 'N/A'):<30} | {model.get('name', 'Unbekannt')}")
                    
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
