# Mammouth.ai Coding Skill

Code-Generierung mit Claude Opus 4-6 via Mammouth.ai API.

## ⚠️ Wichtig

- ✅ **NUR für Code-Generierung**
- ❌ **NIE für Chat, Exec, Thinking, Web-Suche**
- Default für alles andere: Qwen

## Schnellstart

```bash
# Script generieren (Standard: claude-opus-4-6)
python3 scripts/mammouth_coder.py "Erstelle ein Script für..."

# Mit anderem Modell
python3 scripts/mammouth_coder.py "Beschreibung..." --model claude-sonnet-4-6

# Mit Retry-Versuchen
python3 scripts/mammouth_coder.py "Beschreibung..." --retries 3

# Ausgabe in Datei
python3 scripts/mammouth_coder.py "Flask API erstellen" -o api.py
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
MAMMOUTH_API_KEY=dein_mammouth_api_key
```

**API Key holen:** https://mammouth.ai/

## Features

- 🎯 Claude Opus 4-6 für bestes Coding
- 🔄 Retry-Mechanismus mit Exponential Backoff
- 📝 Automatische Dokumentation
- 🛡️ Bessere Fehlerbehandlung

## Python API

```python
from scripts.mammouth_coder import generate_code

code = generate_code(
    "Erstelle eine Python-Klasse für Benutzerverwaltung",
    language="python",
    retries=2
)
print(code)
```

## Fehlerbehandlung

| Exception | Ursache |
|-----------|---------|
| `MammouthAPIKeyError` | Kein API Key |
| `MammouthAPIError` | API-Fehler (HTTP 4xx/5xx) |
| `MammouthResponseError` | Ungültige Antwort |

---

*Teil der OpenClaw Skills Collection* 🎩
