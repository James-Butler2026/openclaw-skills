# Tavily Search Skill

Websuche via Tavily API - AI-generierte Zusammenfassungen mit Quellen.

## Features

- 🔍 **AI-generierte Zusammenfassungen**
- 📊 **Relevance Scores** für jedes Ergebnis
- 🔗 **Strukturierte Ergebnisse** mit Quellenangaben
- 🎯 **Priorität 1** für alle Websuchen

## Schnellstart

```bash
# Standard-Suche
python3 scripts/tavily_search.py "Was ist die Hauptstadt von Frankreich?"

# Erweiterte Suche mit mehr Ergebnissen
python3 scripts/tavily_search.py "KI Entwicklungen 2026" --depth advanced --max-results 10

# Raw JSON output
python3 scripts/tavily_search.py "Python best practices" --raw
```

## Parameter

| Argument | Beschreibung | Default |
|----------|-------------|---------|
| `query` | Suchanfrage (erforderlich) | - |
| `--depth` | Tiefe: `basic` oder `advanced` | `basic` |
| `--max-results` | Anzahl Ergebnisse (1-20) | 5 |
| `--no-answer` | Keine AI-Zusammenfassung | False |
| `--raw` | Raw JSON Output | False |

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
TAVILY_API_KEY=tvly-dein_key_hier
```

**API Key holen:** https://tavily.com/

## Python API

```python
from scripts.tavily_search import search

results = search(
    query="KI Entwicklungen",
    depth="advanced",
    max_results=10
)
print(results)
```

## Vergleich: Tavily vs Perplexity

| Feature | Tavily | Perplexity |
|---------|--------|------------|
| **Priorität** | **1 (Primär)** | 2 (nur auf Anweisung) |
| Typ | Index-basiert | Live-Suche |
| Geschwindigkeit | ⚡ Schnell | ⚡ Schnell |
| Struktur | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Regel:** Immer zuerst Tavily nutzen. Perplexity nur wenn explizit gefordert.

---

*Teil der OpenClaw Skills Collection* 🎩
