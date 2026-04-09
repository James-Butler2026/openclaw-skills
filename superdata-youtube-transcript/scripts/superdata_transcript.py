#!/usr/bin/env python3
"""
Supadata API Wrapper für YouTube-Transkripte
Holt Transkripte und erstellt KI-Zusammenfassungen

WICHTIG: Free Plan = 100 Credits/Monat
1 Video-Transkript = 1 Credit (nur bei Erfolg!)
KEINE Credits für Videos ohne Transkript (404)
"""

import os
import sys
import json
import urllib.request
import urllib.error
import ssl
from pathlib import Path

# API Key aus .env laden
def load_api_key():
    """Lädt SUPERDATA_API_KEY aus .env"""
    env_paths = [
        Path('/home/node/.openclaw/workspace/.env'),
        Path(__file__).parent.parent.parent.parent / '.env',
        Path(__file__).parent.parent.parent / '.env',
        Path('.env')
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip().startswith('SUPERDATA_API_KEY='):
                        return line.strip().split('=', 1)[1].strip().strip('"\'')
    
    return os.getenv('SUPERDATA_API_KEY')


class SuperDataClient:
    """Client für Supadata YouTube Transkript API"""
    
    BASE_URL = "https://api.supadata.ai/v1"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or load_api_key()
        if not self.api_key:
            raise ValueError("SUPERDATA_API_KEY nicht gefunden!")
        
        # SSL Context für API
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def get_transcript(self, video_id: str, language: str = "de") -> dict:
        """
        Holt das Transkript für ein YouTube-Video
        
        Args:
            video_id: YouTube Video ID
            language: Sprachcode (default: "de")
        
        Returns:
            dict mit transcript, content, etc.
        """
        url = f"{self.BASE_URL}/youtube/transcript?videoId={video_id}&language={language}"
        
        req = urllib.request.Request(
            url,
            headers={
                'x-api-key': self.api_key,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            },
            method='GET'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    "success": True,
                    "has_transcript": True,
                    "video_id": video_id,
                    "language": data.get("lang", language),
                    "available_languages": data.get("availableLangs", []),
                    "content": data.get("content", [])
                }
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    "success": False,
                    "error": "No transcript available",
                    "has_transcript": False,
                    "video_id": video_id
                }
            elif e.code == 401:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "has_transcript": False
                }
            elif e.code == 402:
                return {
                    "success": False,
                    "error": "Credits exhausted",
                    "has_transcript": False,
                    "credits_exhausted": True
                }
            else:
                error_body = e.read().decode('utf-8')
                return {
                    "success": False,
                    "error": f"HTTP {e.code}: {error_body[:200]}",
                    "has_transcript": False
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "has_transcript": False
            }
    
    def get_transcript_text(self, video_id: str, language: str = "de") -> str:
        """Holt nur den Transkript-Text (zusammengefügt)"""
        result = self.get_transcript(video_id, language)
        
        if not result.get("has_transcript"):
            return ""
        
        content = result.get("content", [])
        texts = [segment.get("text", "") for segment in content]
        return " ".join(texts)
    
    def summarize_transcript(self, transcript_text: str, video_title: str = "") -> str:
        """
        Erstellt eine kurze Zusammenfassung des Transkripts
        Nutzt Qwen für die Zusammenfassung
        """
        max_len = 4000
        if len(transcript_text) > max_len:
            transcript_text = transcript_text[:max_len] + "..."
        
        prompt = f"""Fasse das folgende YouTube-Video-Transkript kurz und prägnant zusammen (2-3 Sätze, maximal 250 Zeichen).

Titel: {video_title or 'YouTube Video'}

Transkript:
{transcript_text}

Zusammenfassung:"""

        try:
            import subprocess
            
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/generate',
                 '-d', json.dumps({
                     "model": "qwen3.5:cloud",
                     "prompt": prompt,
                     "stream": False,
                     "options": {"temperature": 0.3, "num_predict": 150}
                 })],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                summary = response.get('response', '').strip()
                if summary:
                    return summary
            
        except Exception as e:
            print(f"LLM Summarization failed: {e}", file=sys.stderr)
        
        # Fallback
        sentences = transcript_text.split('. ')[:3]
        return '. '.join(sentences) + '.' if sentences else "Zusammenfassung nicht verfügbar"
    
    def get_video_summary(self, video_id: str, video_title: str = "", language: str = "de") -> dict:
        """
        Haupt-Methode: Holt Transkript und gibt Zusammenfassung zurück
        """
        result = self.get_transcript(video_id, language)
        
        if not result.get('has_transcript'):
            return {
                "success": True,
                "has_transcript": False,
                "video_id": video_id,
                "reason": result.get('error', 'No transcript available')
            }
        
        transcript_text = self.get_transcript_text(video_id, language)
        summary = self.summarize_transcript(transcript_text, video_title)
        
        return {
            "success": True,
            "has_transcript": True,
            "video_id": video_id,
            "summary": summary,
            "transcript": transcript_text,
            "transcript_length": len(transcript_text),
            "language": result.get("language", language)
        }


def main():
    """CLI-Test"""
    if len(sys.argv) < 2:
        print("Usage: python3 superdata_transcript.py <video_id> [video_title]")
        print("Example: python3 superdata_transcript.py dQw4w9WgXcQ 'Never Gonna Give You Up'")
        return 1
    
    video_id = sys.argv[1]
    video_title = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🔍 Prüfe Transkript für Video: {video_id}")
    
    client = SuperDataClient()
    result = client.get_video_summary(video_id, video_title)
    
    if result.get('has_transcript'):
        print(f"✅ Transkript gefunden!")
        print(f"   Sprache: {result.get('language', 'de')}")
        print(f"   Länge: {result['transcript_length']} Zeichen")
        print(f"\n📝 Zusammenfassung:")
        print(result['summary'])
    else:
        print(f"❌ Kein Transkript verfügbar")
        print(f"   Grund: {result.get('reason', 'Unbekannt')}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
