# Tavily Search Skill

Websuche via Tavily API – mit KI-generierten Zusammenfassungen.

## Features

- 🔍 AI-generierte Zusammenfassungen
- 📊 Relevance Scores
- 📋 Strukturierte Ergebnisse
- 📚 Quellenangaben

## Installation

```bash
cd ~/.openclaw/workspace/skills/tavily-search/
```

## Verwendung

```bash
# Einfache Suche
python3 scripts/tavily_search.py "Was ist die Hauptstadt von Frankreich?"

# Erweiterte Suche
python3 scripts/tavily_search.py "KI Entwicklungen 2026" \
    --depth advanced --max-results 10

# In Python nutzen
from scripts.tavily_search import search
results = search("Python Tutorial", max_results=5)
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Key holen:** https://tavily.com

## Sicherheit

- API-Key niemals committen
- Suchanfragen werden verarbeitet
- Keine persönlichen Daten speichern

---
*Websuche für OpenClaw* 🔍
