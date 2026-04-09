#!/usr/bin/env python3
"""
YouTube Transkript via SuperData API
Credits-schonende Implementierung für Free Plan (100 Credits/Monat)

REGELN:
- Nur 1 Credit pro Video mit verfügbarem Transkript
- KEINE Credits für Videos ohne Transkript (wenn API 404 zurückgibt)
- Monatliches Credit-Tracking (max 100)
- Cache um Duplikate zu vermeiden
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# SuperData Client importieren
sys.path.insert(0, str(Path(__file__).parent))
from superdata_transcript import SuperDataClient

CREDIT_FILE = Path("/home/node/.openclaw/workspace/memory/superdata_credits.json")
TRANSCRIPT_CACHE = Path("/home/node/.openclaw/workspace/memory/superdata_cache.json")

MAX_CREDITS_PER_MONTH = 100
WARNING_THRESHOLD = 80


def load_credit_state():
    """Lädt aktuellen Credit-Status"""
    if CREDIT_FILE.exists():
        try:
            with open(CREDIT_FILE) as f:
                state = json.load(f)
                # Reset wenn neuer Monat
                current_month = datetime.now().strftime("%Y-%m")
                if state.get("month") != current_month:
                    return {
                        "month": current_month,
                        "used": 0,
                        "remaining": MAX_CREDITS_PER_MONTH,
                        "videos_processed": []
                    }
                return state
        except:
            pass
    
    return {
        "month": datetime.now().strftime("%Y-%m"),
        "used": 0,
        "remaining": MAX_CREDITS_PER_MONTH,
        "videos_processed": []
    }


def save_credit_state(state):
    """Speichert Credit-Status"""
    CREDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CREDIT_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_cache():
    """Lädt Transkript-Cache (um Duplikate zu vermeiden)"""
    if TRANSCRIPT_CACHE.exists():
        try:
            with open(TRANSCRIPT_CACHE) as f:
                return json.load(f)
        except:
            pass
    return {}


def save_cache(cache):
    """Speichert Transkript-Cache"""
    TRANSCRIPT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    # Cleanup: Entferne Einträge älter als 30 Tage
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    cache = {k: v for k, v in cache.items() if v.get("checked_at", "") > cutoff}
    with open(TRANSCRIPT_CACHE, "w") as f:
        json.dump(cache, f, indent=2)


def get_transcript_summary(video_id: str, video_title: str = "", language: str = "de") -> Optional[dict]:
    """
    Holt Transkript-Zusammenfassung für ein YouTube-Video
    
    Args:
        video_id: YouTube Video ID
        video_title: Titel für Kontext
        language: Sprache (default: de)
    
    Returns:
        dict mit summary, is_generated, etc. oder None wenn:
        - Kein Transkript verfügbar
        - Credits aufgebraucht
        - Bereits verarbeitet (Cache)
    """
    
    # Credit-Status prüfen
    credit_state = load_credit_state()
    if credit_state["remaining"] <= 0:
        print(f"   ⚠️  SuperData Credits aufgebraucht ({credit_state['used']}/{MAX_CREDITS_PER_MONTH})")
        return None
    
    # Cache prüfen
    cache = load_cache()
    if video_id in cache:
        cached = cache[video_id]
        print(f"   ℹ️  Transkript aus Cache (kein Credit verbraucht)")
        if cached.get("has_transcript"):
            return {
                "summary": cached["summary"],
                "source": "cache"
            }
        return None
    
    # Neues Video: SuperData API aufrufen
    try:
        client = SuperDataClient()
        result = client.get_video_summary(video_id, video_title, language)
        
        # Cache-Eintrag erstellen
        cache_entry = {
            "checked_at": datetime.now().isoformat(),
            "has_transcript": result.get("has_transcript", False),
            "video_title": video_title
        }
        
        if result.get("has_transcript"):
            # Credit wurde verbraucht (nur bei Erfolg)
            credit_state["used"] += 1
            credit_state["remaining"] -= 1
            credit_state["videos_processed"].append({
                "video_id": video_id,
                "title": video_title[:50],
                "date": datetime.now().isoformat()
            })
            
            cache_entry.update({
                "summary": result["summary"],
                "source": "superdata"
            })
            
            # Speichern
            cache[video_id] = cache_entry
            save_cache(cache)
            save_credit_state(credit_state)
            
            print(f"   ✅ Transkript erhalten (Credit {credit_state['used']}/{MAX_CREDITS_PER_MONTH})")
            
            return {
                "summary": result["summary"],
                "source": "superdata"
            }
        else:
            # Kein Transkript verfügbar - KEIN Credit verbraucht (wenn API 404)
            # Aber wir speichern im Cache um erneute Anfragen zu vermeiden
            cache[video_id] = cache_entry
            save_cache(cache)
            
            reason = result.get("reason", "Unknown")
            print(f"   ℹ️  Kein Transkript verfügbar: {reason}")
            return None
            
    except Exception as e:
        print(f"   ❌ Fehler bei SuperData: {e}")
        return None


def get_credit_status():
    """Gibt aktuellen Credit-Status zurück"""
    state = load_credit_state()
    return {
        "month": state["month"],
        "used": state["used"],
        "remaining": state["remaining"],
        "limit": MAX_CREDITS_PER_MONTH,
        "percentage": (state["used"] / MAX_CREDITS_PER_MONTH) * 100
    }


def process_new_videos(videos: list, max_videos: int = 3) -> list:
    """
    Verarbeitet neue Videos und fügt Transkript-Zusammenfassungen hinzu
    
    Args:
        videos: Liste neuer Videos
        max_videos: Max Anzahl Videos für Transkription
    
    Returns:
        Liste mit erweiterten Video-Daten
    """
    if not videos:
        return videos
    
    credit_status = get_credit_status()
    print(f"\n💰 SuperData Credits: {credit_status['used']}/{credit_status['limit']} verbraucht")
    
    if credit_status["remaining"] <= 0:
        print("⚠️  Keine Credits mehr verfügbar - überspringe Transkripte")
        return videos
    
    processed = []
    transcripts_fetched = 0
    
    for video in videos[:max_videos]:
        video_id = video.get("id")
        title = video.get("title", "")
        
        if not video_id:
            processed.append(video)
            continue
        
        print(f"\n📝 Prüfe Transkript: {title[:50]}...")
        
        transcript = get_transcript_summary(video_id, title)
        
        if transcript:
            video["transcript_summary"] = transcript["summary"]
            video["transcript_source"] = transcript["source"]
            transcripts_fetched += 1
        else:
            video["transcript_summary"] = None
            video["transcript_source"] = None
        
        processed.append(video)
    
    # Restliche Videos ohne Transkription hinzufügen
    processed.extend(videos[max_videos:])
    
    print(f"\n✅ {transcripts_fetched} Transkripte geholt")
    return processed


if __name__ == "__main__":
    # CLI-Test
    if len(sys.argv) < 2:
        print("Usage: python3 youtube_transcript_superdata.py <video_id> [title]")
        print("       python3 youtube_transcript_superdata.py --status")
        sys.exit(1)
    
    if sys.argv[1] == "--status":
        status = get_credit_status()
        print(f"SuperData Credit Status ({status['month']}):")
        print(f"  Verwendet: {status['used']}/{status['limit']}")
        print(f"  Verbleibend: {status['remaining']}")
        print(f"  Auslastung: {status['percentage']:.1f}%")
        sys.exit(0)
    
    video_id = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"Teste SuperData für Video: {video_id}")
    result = get_transcript_summary(video_id, title)
    
    if result:
        print(f"\n✅ Erfolg!")
        print(f"   Quelle: {result['source']}")
        print(f"   Zusammenfassung:\n{result['summary']}")
    else:
        print("\n❌ Kein Transkript verfügbar oder Fehler")
