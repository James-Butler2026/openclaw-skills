---
name: tavily-search
description: Web search via Tavily API. Use when the user wants to search the web, find current information, research topics, or get answers with sources. Provides AI-generated summaries and structured search results with relevance scores.
---

# Tavily Search

## Overview

**PRIMARY WEB SEARCH TOOL** – Dies ist die bevorzugte Websuche für alle Anfragen.

This skill provides web search capabilities using the Tavily API. It delivers high-quality search results with AI-generated summaries, source URLs, and relevance scores.

## Priorität

| Priorität | Tool | Wann verwenden |
|-----------|------|----------------|
| **1 (Primär)** | **Tavily** | **Immer** – Standard für alle Websuchen |
| 2 | Perplexity | Nur auf **direkte Anweisung** von Eurer Lordschaft |

**WICHTIG (25.03.2026):**
- **Ausschließlich Tavily für Websuche verwenden!**
- Kein `web_search` (Brave API) mehr
- Perplexity nur wenn explizit gefordert

## When to Use

Use this skill when:
- The user asks to search the web or find information online
- Current/recent information is needed (beyond training data cutoff)
- Researching topics, products, people, events, or news
- Fact-checking or finding authoritative sources
- The user wants "the latest" on any topic
- Price comparisons, product searches, deals

## Quick Start

```bash
# Standard-Suche (IMMER diesen Pfad verwenden!)
python3 skills/tavily-search/scripts/tavily_search.py "Was ist die Hauptstadt von Frankreich?"

# Erweiterte Suche mit mehr Ergebnissen
python3 skills/tavily-search/scripts/tavily_search.py "KI Entwicklungen 2026" --depth advanced --max-results 10

# Raw JSON output für Weiterverarbeitung
python3 skills/tavily-search/scripts/tavily_search.py "Python best practices" --raw
```

## Usage

The script supports the following arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `query` | The search query (required) | - |
| `-d, --depth` | Search depth: `basic` or `advanced` | `basic` |
| `-n, --max-results` | Number of results (1-20) | 5 |
| `--no-answer` | Disable AI-generated summary | False |
| `--raw` | Output raw JSON | False |

## API Key

The Tavily API key is configured in `/home/node/.openclaw/workspace/.env`:
```
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
```

**To get a key:** https://tavily.com/

## Important Rules

1. **Tavily ist immer die erste Wahl** für Websuche
2. **Perplexity nur auf direkte Anweisung** (z.B. "Such mir das mit Perplexity")
3. **NIE `web_search` (Brave)** verwenden
4. Bei Preisen: Ergebnisse als Orientierung sehen, immer verifizieren

## Perplexity (Nur auf Anweisung!)

**Status: ✅ VERFÜGBAR** (getestet 25.03.2026)

Perplexity ist über Mammouth.ai erreichbar und funktioniert einwandfrei. **ABER:** Nur verwenden wenn Euer explizit "Perplexity" sagt!

### Verfügbare Modelle
| Modell | Verwendung |
|--------|------------|
| `sonar-pro` | Standard Live-Suche |
| `sonar-deep-research` | Tiefe Recherche |
| `sonar-reasoning-pro` | Websuche + logische Analyse |

### Unterschied zu Tavily
- **Tavily:** Index-basiert (schnell, strukturiert)
- **Perplexity:** Echte Live-Suche (aktueller, mit Quellenangaben)

### Code-Beispiel (nur auf Anweisung!)
```python
import json
import urllib.request

# Perplexity via Mammouth.ai
def perplexity_search(query, model="sonar-pro"):
    api_key = "sk-mammouth-..."  # Aus .env laden
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Suche nach aktuellen Informationen."},
            {"role": "user", "content": query}
        ],
        "max_tokens": 1000
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://mammouth.ai",
        "Referer": "https://mammouth.ai/"
    }
    req = urllib.request.Request(
        "https://api.mammouth.ai/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
        return data['choices'][0]['message']['content']
```

## Known Limitations

- **Price searches** may return outdated or inaccurate results
- Always verify prices directly on the seller's website
- For time-sensitive data (prices, availability), use as starting point only
- Tavily liefert manchmal ältere Index-Daten (nicht live wie Perplexity)

## Examples

### Product Search
```bash
python3 skills/tavily-search/scripts/tavily_search.py \
  "Product XYZ best price" --depth advanced --max-results 10
```

### Current Events
```bash
python3 skills/tavily-search/scripts/tavily_search.py \
  "latest news today" --depth advanced --max-results 5
```

## Resources

### scripts/
- `tavily_search.py` - Main search script with formatted output

### Documentation
- API Docs: https://docs.tavily.com/
- Dashboard: https://app.tavily.com/

## Changelog

- **25.03.2026:** Dokumentation aktualisiert – Primär-Tool für Websuche
- **25.03.2026:** Perplexity-Integration dokumentiert (nur auf Anweisung!)
