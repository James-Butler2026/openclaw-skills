#!/usr/bin/env python3
"""
ElevenLabs TTS Test - Drachenlord Voice
Test-Datei für Sprachnachrichten-Generierung
"""

import os
import sys
import time

# Setup paths
sys.path.insert(0, '/home/node/.openclaw/workspace')

from scripts.elevenlabs_tts import generate_speech, load_api_key

# Drachenlord Voice Settings
DRACHENLORD_VOICE = "NkhHdPbLqYzmdIaSUuIy"
DRACHENLORD_SETTINGS = {
    "stability": 0.35,
    "similarity_boost": 0.85,
    "style": 0.45,
    "use_speaker_boost": True
}


def generate_voice_message(text, output_path="/tmp/elevenlabs_test.mp3"):
    """
    Generiert eine Sprachnachricht mit Drachenlord-Stimme
    
    Args:
        text: Zu sprechender Text
        output_path: Ausgabepfad für MP3
    
    Returns:
        dict mit info über die Generierung
    """
    api_key = load_api_key()
    
    if not api_key:
        return {"error": "Kein API Key gefunden"}
    
    # Zeichen zählen
    char_count = len(text)
    
    # Timer starten
    start_time = time.time()
    
    # Generieren
    result = generate_speech(
        api_key=api_key,
        text=text,
        voice_id=DRACHENLORD_VOICE,
        model="eleven_multilingual_v2",
        output_path=output_path,
        voice_settings=DRACHENLORD_SETTINGS
    )
    
    # Timer stoppen
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    
    if result:
        file_size = os.path.getsize(result)
        return {
            "success": True,
            "output_path": result,
            "characters": char_count,
            "duration_seconds": duration,
            "file_size_bytes": file_size,
            "voice": DRACHENLORD_VOICE,
            "settings": DRACHENLORD_SETTINGS
        }
    else:
        return {
            "success": False,
            "error": "Generierung fehlgeschlagen",
            "characters": char_count,
            "duration_seconds": duration
        }


def format_stats(info):
    """Formatiert die Statistiken für die Nachricht"""
    if info.get("success"):
        return f"[{info['characters']} Zeichen | Gesamt: {info['characters']} | {info['duration_seconds']}s]"
    return "[FEHLER]"


if __name__ == "__main__":
    # Test-Text
    test_text = "hey kosta, etzala wirf mayans mc rein"
    
    print("🎙️  ElevenLabs TTS Test - Drachenlord Voice")
    print("=" * 50)
    print(f"Text: {test_text}")
    print(f"Voice: {DRACHENLORD_VOICE}")
    print(f"Settings: {DRACHENLORD_SETTINGS}")
    print("-" * 50)
    
    # Generieren
    result = generate_voice_message(test_text)
    
    if result["success"]:
        print(f"✅ Erfolgreich!")
        print(f"   Output: {result['output_path']}")
        print(f"   Größe: {result['file_size_bytes']} bytes")
        print(f"   Stats: {format_stats(result)}")
        print(f"\n🐉 Drachenlord hat gesprochen!")
    else:
        print(f"❌ Fehler: {result.get('error', 'Unbekannt')}")
        sys.exit(1)
