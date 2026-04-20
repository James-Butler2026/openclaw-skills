#!/usr/bin/env python3
"""
ElevenLabs TTS mit Statistik-Tracking
Speichert Gesamtverbrauch über alle Anfragen
"""

import os
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, "/home/node/.openclaw/workspace")
from scripts.elevenlabs_tts import generate_speech, load_api_key

# Stats File
STATS_FILE = "/home/node/.openclaw/workspace/data/elevenlabs_stats.json"


def load_stats():
    """Lädt die aktuelle Statistik"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        "total_characters": 0,
        "total_requests": 0,
        "total_duration_seconds": 0,
        "first_used": time.strftime("%Y-%m-%d %H:%M"),
        "last_used": None
    }


def save_stats(stats):
    """Speichert die Statistik"""
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)


def generate_with_stats(text, voice_id="NkhHdPbLqYzmdIaSUuIy"):
    """Generiert Sprache mit Statistik-Tracking"""
    
    api_key = load_api_key()
    if not api_key:
        return None, "Kein API Key"
    
    # Konstantin's Settings - etwas schneller
    voice_settings = {
        "stability": 1.0,
        "similarity_boost": 0.9,
        "style": 0.1,
        "use_speaker_boost": True,
        "speed": 0.85
    }
    
    char_count = len(text)
    
    # Generieren
    start = time.time()
    result = generate_speech(
        api_key=api_key,
        text=text,
        voice_id=voice_id,
        model="eleven_multilingual_v2",
        output_path="/tmp/elevenlabs_latest.mp3",
        voice_settings=voice_settings
    )
    duration = round(time.time() - start, 2)
    
    if result:
        # Stats updaten
        stats = load_stats()
        stats["total_characters"] += char_count
        stats["total_requests"] += 1
        stats["total_duration_seconds"] += duration
        stats["last_used"] = time.strftime("%Y-%m-%d %H:%M")
        save_stats(stats)
        
        return {
            "success": True,
            "output_path": result,
            "this_characters": char_count,
            "this_duration": duration,
            "total_characters": stats["total_characters"],
            "total_requests": stats["total_requests"]
        }, None
    else:
        return None, "Generierung fehlgeschlagen"


if __name__ == "__main__":
    # Test
    text = "Etzala, ich bin der Drachenlord. Willkommen auf meinem Discord, Kosta. Passt auf euch auf, ja?"
    
    print(f"🎙️  Drachenlord TTS mit Statistik")
    print(f"Text: {text}")
    print("-" * 50)
    
    result, error = generate_with_stats(text)
    
    if result:
        print(f"✅ Erfolgreich!")
        print(f"\n📊 DIESE ANFRAGE:")
        print(f"   Zeichen: {result['this_characters']}")
        print(f"   Dauer: {result['this_duration']}s")
        print(f"\n📈 GESAMT-STATISTIK:")
        print(f"   Gesamtzeichen: {result['total_characters']}")
        print(f"   Anzahl Anfragen: {result['total_requests']}")
        print(f"   Durchschnitt: {result['total_characters'] // result['total_requests']} Zeichen/Anfrage")
        print(f"\n💾 Gespeichert unter: {STATS_FILE}")
    else:
        print(f"❌ Fehler: {error}")
        sys.exit(1)
