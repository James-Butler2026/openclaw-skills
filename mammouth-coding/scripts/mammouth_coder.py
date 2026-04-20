#!/usr/bin/env python3
"""
Mammouth.ai Coder
=================
NUR für Code-Generierung!

Verwendet Claude Opus 4.6 (Standard) für hochwertigen Code.
Andere Modelle verfügbar: claude-sonnet-4-6, sonar-pro, etc.

Verbessert mit:
- Zentralem Logging
- Bessere Fehlerbehandlung mit spezifischen Exceptions
- Retry-Mechanismus bei API-Fehlern
- Exit-Codes für Script-Integration
"""

import os
import sys
import json
import urllib.request
import urllib.error
import time
from pathlib import Path
from typing import Optional

# Zentrales Logging importieren
sys.path.insert(0, '/home/node/.openclaw/workspace/scripts')
from logger_config import get_logger

logger = get_logger(__name__)

MAMMOUTH_API_URL = "https://api.mammouth.ai/v1/chat/completions"
DEFAULT_MODEL = "claude-opus-4-6"

# Exit-Codes
EXIT_SUCCESS = 0
EXIT_NO_API_KEY = 1
EXIT_API_ERROR = 2
EXIT_INVALID_RESPONSE = 3


class MammouthError(Exception):
    """Base-Exception für Mammouth-Fehler"""
    pass


class MammouthAPIKeyError(MammouthError):
    """API Key nicht gefunden oder ungültig"""
    pass


class MammouthAPIError(MammouthError):
    """API-Fehler (HTTP 4xx/5xx)"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class MammouthResponseError(MammouthError):
    """Ungültige API-Antwort"""
    pass


def load_api_key() -> str:
    """
    Lädt Mammouth API Key aus .env.
    
    Returns:
        API Key als String
    
    Raises:
        MammouthAPIKeyError: Wenn kein gültiger Key gefunden
    """
    env_path = Path("/home/node/.openclaw/workspace/.env")
    
    if env_path.exists():
        try:
            with open(env_path) as f:
                for line in f:
                    if line.startswith("MAMMOUTH_API_KEY="):
                        key = line.strip().split("=", 1)[1]
                        # Überspringe Platzhalter
                        if key and not key.endswith('...'):
                            logger.debug("Mammouth API Key aus .env geladen")
                            return key
        except (OSError, PermissionError) as e:
            logger.warning(f"Konnte .env nicht lesen: {e}")
    
    # Fallback: Umgebungsvariable
    api_key = os.getenv("MAMMOUTH_API_KEY")
    if api_key:
        logger.debug("Mammouth API Key aus Umgebungsvariable geladen")
        return api_key
    
    raise MammouthAPIKeyError(
        "MAMMOUTH_API_KEY nicht gefunden. Bitte fügen Sie ihn zur .env Datei hinzu: "
        "MAMMOUTH_API_KEY=sk-mammouth-..."
    )


def generate_code(
    prompt: str,
    language: str = "python",
    model: str = DEFAULT_MODEL,
    max_retries: int = 2,
    timeout: int = 120
) -> Optional[str]:
    """
    Generiert Code mit Mammouth.ai.
    
    Args:
        prompt: Die Code-Beschreibung
        language: Programmiersprache (python, bash, javascript, etc.)
        model: Das zu verwendende Modell (claude-opus-4-6, etc.)
        max_retries: Anzahl der Retry-Versuche bei Fehlern
        timeout: Timeout in Sekunden
    
    Returns:
        Generierter Code als String, oder None bei Fehler
    
    Raises:
        MammouthAPIKeyError: Wenn kein API Key
        MammouthAPIError: Bei API-Fehlern
        MammouthResponseError: Bei ungültiger Antwort
    """
    api_key = load_api_key()
    
    if not api_key:
        raise MammouthAPIKeyError("Kein API Key verfügbar")
    
    system_prompt = f"""Du bist ein erfahrener Software-Entwickler.
Erstelle hochwertigen, gut dokumentierten {language}-Code.

Regeln:
- Kommentiere wichtige Stellen
- Nutze Best Practices
- Fehlerbehandlung einbauen
- Nur Code ausgeben, keine Erklärungen außerhalb des Codes"""
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://mammouth.ai",
        "Referer": "https://mammouth.ai/"
    }
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry-Versuch {attempt}/{max_retries}...")
                time.sleep(2 ** attempt)  # Exponentielles Backoff
            
            logger.info(f"Sende Request an Mammouth.ai (Modell: {model})")
            
            req = urllib.request.Request(
                MAMMOUTH_API_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                logger.info(f"Response: HTTP {response.status}")
                data = json.loads(response.read().decode('utf-8'))
                
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    logger.info("Code erfolgreich generiert")
                    return content
                else:
                    raise MammouthResponseError(f"Ungültige Antwortstruktur: {data.keys()}")
                    
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP Fehler {e.code}: {e.reason}"
            logger.error(error_msg)
            last_error = MammouthAPIError(error_msg, status_code=e.code)
            
            # Bei 401/403 nicht retryen (Auth-Fehler)
            if e.code in (401, 403):
                raise last_error
                
            try:
                error_body = e.read().decode()
                logger.error(f"API Fehler-Details: {error_body[:500]}")
            except:
                pass
                
        except urllib.error.URLError as e:
            error_msg = f"Verbindungsfehler: {e.reason}"
            logger.error(error_msg)
            last_error = MammouthAPIError(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON Fehler: {e}"
            logger.error(error_msg)
            last_error = MammouthResponseError(error_msg)
    
    # Alle Retries aufgebraucht
    if last_error:
        raise last_error
    
    return None


def main() -> int:
    """
    Hauptfunktion für CLI-Nutzung.
    
    Returns:
        Exit-Code (0 = Erfolg, >0 = Fehler)
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Mammouth.ai Coder - Hochwertige Code-Generierung',
        epilog='Beispiel: python3 mammouth_coder.py "Erstelle eine REST API"'
    )
    
    parser.add_argument('prompt', help='Was soll programmiert werden?')
    parser.add_argument('--language', '-l', default='python', help='Programmiersprache')
    parser.add_argument('--model', '-m', default=DEFAULT_MODEL, help=f'KI-Modell (Standard: {DEFAULT_MODEL})')
    parser.add_argument('--output', '-o', help='Ausgabedatei')
    parser.add_argument('--retries', '-r', type=int, default=2, help='Anzahl der Retry-Versuche (Standard: 2)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Ausführliche Logging-Ausgabe')
    
    args = parser.parse_args()
    
    # Logging-Level anpassen
    if args.verbose:
        logger.setLevel('DEBUG')
    
    try:
        print("🔧 Mammouth.ai Coder")
        print(f"📝 Prompt: {args.prompt}")
        print(f"🤖 Modell: {args.model}")
        print("=" * 60)
        
        code = generate_code(
            prompt=args.prompt,
            language=args.language,
            model=args.model,
            max_retries=args.retries
        )
        
        if code:
            print("\n✅ ERFOLG!")
            print("=" * 60)
            print(code)
            print("=" * 60)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(code)
                logger.info(f"Code gespeichert in: {args.output}")
                print(f"\n💾 Gespeichert in: {args.output}")
            
            return EXIT_SUCCESS
        else:
            print("\n❌ Kein Code generiert")
            return EXIT_INVALID_RESPONSE
            
    except MammouthAPIKeyError as e:
        logger.error(str(e))
        print(f"\n❌ {e}")
        return EXIT_NO_API_KEY
        
    except MammouthAPIError as e:
        logger.error(str(e))
        print(f"\n❌ API Fehler: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        return EXIT_API_ERROR
        
    except MammouthResponseError as e:
        logger.error(str(e))
        print(f"\n❌ Antwort-Fehler: {e}")
        return EXIT_INVALID_RESPONSE
        
    except Exception as e:
        logger.exception("Unerwarteter Fehler")
        print(f"\n❌ Ein unerwarteter Fehler ist aufgetreten: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
