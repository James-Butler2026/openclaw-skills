#!/usr/bin/env python3
"""
Tavily Search Script
Euer persönlicher Butler für erstklassige Websuche.
API Key wird aus .env Datei geladen.

Verbessert mit:
- Zentralem Logging
- Bessere Fehlerbehandlung
- Exit-Codes für Script-Integration
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# Zentrales Logging importieren
sys.path.insert(0, '/home/node/.openclaw/workspace/scripts')
from logger_config import get_logger

logger = get_logger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"

# Exit-Codes für bessere Fehlerbehandlung
EXIT_SUCCESS = 0
EXIT_NO_API_KEY = 1
EXIT_HTTP_ERROR = 2
EXIT_CONNECTION_ERROR = 3
EXIT_JSON_ERROR = 4
EXIT_NO_RESULTS = 5


class TavilySearchError(Exception):
    """Base-Exception für Tavily-Suchfehler"""
    pass


class TavilyAPIKeyError(TavilySearchError):
    """API Key nicht gefunden oder ungültig"""
    pass


class TavilyConnectionError(TavilySearchError):
    """Verbindungsprobleme zur API"""
    pass


class TavilyResponseError(TavilySearchError):
    """Ungültige Antwort von der API"""
    pass


def load_api_key() -> str:
    """
    Lädt Tavily API Key aus .env Datei.
    
    Returns:
        API Key als String
    
    Raises:
        TavilyAPIKeyError: Wenn kein Key gefunden
    """
    env_path = Path("/home/node/.openclaw/workspace/.env")
    
    # Versuche aus .env zu laden
    if env_path.exists():
        try:
            with open(env_path) as f:
                for line in f:
                    if line.startswith("TAVILY_API_KEY="):
                        key = line.strip().split("=", 1)[1]
                        # Überspringe Platzhalter
                        if key and not key.endswith("tvly-xxxxxxxxxxxxxxxxxxxxxxxx"):
                            logger.debug("API Key aus .env geladen")
                            return key
        except (OSError, PermissionError) as e:
            logger.warning(f"Konnte .env nicht lesen: {e}")
    
    # Fallback: Umgebungsvariable
    api_key = os.getenv("TAVILY_API_KEY")
    if api_key:
        logger.debug("API Key aus Umgebungsvariable geladen")
        return api_key
    
    raise TavilyAPIKeyError(
        "TAVILY_API_KEY nicht gefunden. Bitte fügen Sie ihn zur .env Datei hinzu: "
        "TAVILY_API_KEY=tvly-..."
    )


def search_tavily(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_answer: bool = True,
    include_images: bool = False
) -> dict:
    """
    Führt eine Suche über die Tavily API durch.
    
    Args:
        query: Der Suchbegriff
        search_depth: "basic" oder "advanced"
        max_results: Anzahl der Ergebnisse (1-20)
        include_answer: True für eine KI-generierte Zusammenfassung
        include_images: True um Bilder zu includieren
    
    Returns:
        JSON-Daten der API-Antwort
    
    Raises:
        TavilyAPIKeyError: Wenn kein API Key gefunden
        TavilyConnectionError: Bei Verbindungsproblemen
        TavilyResponseError: Bei ungültiger API-Antwort
    """
    api_key = load_api_key()
    
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_answer": include_answer,
        "include_images": include_images,
        "include_raw_content": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Starte Tavily-Suche: '{query[:50]}...'")
        
        req = urllib.request.Request(
            TAVILY_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode('utf-8'))
            logger.info(f"Suche erfolgreich: {len(data.get('results', []))} Ergebnisse")
            return data
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Fehler {e.code}: {e.reason}"
        logger.error(error_msg)
        try:
            error_body = e.read().decode('utf-8')
            logger.error(f"API Fehler-Details: {error_body[:500]}")
        except:
            pass
        raise TavilyResponseError(error_msg)
        
    except urllib.error.URLError as e:
        error_msg = f"Verbindungsfehler: {e.reason}"
        logger.error(error_msg)
        raise TavilyConnectionError(error_msg)
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON Fehler: {e}"
        logger.error(error_msg)
        raise TavilyResponseError(error_msg)


def format_results(data: dict) -> str:
    """
    Formatiert die Suchergebnisse hübsch für die Lordschaft.
    
    Args:
        data: JSON-Daten der API-Antwort
    
    Returns:
        Formatierte Ausgabe als String
    """
    lines = []
    lines.append("\n" + "="*60)
    lines.append(f"🎩 Suchergebnisse für: '{data.get('query', 'Unbekannt')}'")
    lines.append("="*60 + "\n")
    
    # KI-Antwort anzeigen, falls vorhanden
    answer = data.get('answer')
    if answer:
        lines.append("📋 Zusammenfassung:")
        lines.append("-" * 40)
        lines.append(answer)
        lines.append("-" * 40)
        lines.append("")
    
    # Ergebnisse anzeigen
    results = data.get('results', [])
    if not results:
        lines.append("🎩 *Verbeugt sich bedauernd* Leider keine Ergebnisse gefunden, Eure Lordschaft.")
        return "\n".join(lines)
    
    lines.append(f"🔍 {len(results)} Ergebnisse gefunden:\n")
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'Kein Titel')
        url = result.get('url', 'Keine URL')
        content = result.get('content', 'Keine Beschreibung verfügbar')
        score = result.get('score', 0)
        
        lines.append(f"  {i}. {title}")
        lines.append(f"     URL: {url}")
        lines.append(f"     Relevanz: {score:.2f}")
        lines.append(f"     {content[:200]}{'...' if len(content) > 200 else ''}")
        lines.append("")
    
    lines.append("="*60)
    lines.append("🎩 Euer ergebenster Butler hat die Suche beendet.")
    lines.append("="*60 + "\n")
    
    return "\n".join(lines)


def main() -> int:
    """
    Hauptfunktion für CLI-Nutzung.
    
    Returns:
        Exit-Code (0 = Erfolg, >0 = Fehler)
    """
    parser = argparse.ArgumentParser(
        description="Tavily Websuche - Euer persönlicher Butler",
        epilog="Beispiel: python3 tavily_search.py 'Was ist die Hauptstadt von Frankreich?'"
    )
    
    parser.add_argument('query', help='Der Suchbegriff')
    parser.add_argument('-d', '--depth', choices=['basic', 'advanced'], 
                        default='basic', help='Suchtiefe (basic oder advanced)')
    parser.add_argument('-n', '--max-results', type=int, default=5,
                        help='Anzahl der Ergebnisse (1-20, Standard: 5)')
    parser.add_argument('--no-answer', action='store_true',
                        help='Keine KI-Zusammenfassung anzeigen')
    parser.add_argument('--raw', action='store_true',
                        help='Rohdaten als JSON ausgeben')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Ausführliche Logging-Ausgabe')
    
    args = parser.parse_args()
    
    # Logging-Level anpassen
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Suche durchführen
        data = search_tavily(
            query=args.query,
            search_depth=args.depth,
            max_results=args.max_results,
            include_answer=not args.no_answer
        )
        
        if args.raw:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(format_results(data))
        
        return EXIT_SUCCESS
        
    except TavilyAPIKeyError as e:
        logger.error(str(e))
        print(f"🎩 *Hustet höflich* {e}")
        return EXIT_NO_API_KEY
        
    except TavilyConnectionError as e:
        logger.error(str(e))
        print(f"🎩 *Schluckt nervös* {e}")
        return EXIT_CONNECTION_ERROR
        
    except TavilyResponseError as e:
        logger.error(str(e))
        print(f"🎩 *Räuspert sich verlegen* {e}")
        return EXIT_HTTP_ERROR
        
    except Exception as e:
        logger.exception("Unerwarteter Fehler")
        print(f"🎩 *Wirft verstohlen einen Blick auf die Uhr* Ein unerwarteter Fehler: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
