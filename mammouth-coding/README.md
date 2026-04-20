# Mammouth Coding Skill

Code-Generierung mit Claude Opus 4-6 via Mammouth.ai API.

## Features

- 🤖 Claude Opus 4-6 für hochwertigen Code
- 🔄 Retry-Mechanismus
- 🛡️ Bessere Fehlerbehandlung
- 📋 Automatische Dokumentation

## Installation

```bash
cd ~/.openclaw/workspace/skills/mammouth-coding/
```

## Verwendung

```bash
# Code generieren
python3 scripts/mammouth_coder.py "Erstelle eine Python-Klasse"

# Mit Sprache
python3 scripts/mammouth_coder.py "Erstelle eine Bash-Funktion" --language bash

# Speichern
python3 scripts/mammouth_coder.py "Flask API" --output api.py
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
MAMMOUTH_API_KEY=sk-mammouth-xxxxxxxxxxxxxxxxxxxxxxxx
```

**NUR für Code-Generierung verwenden!**

## Sicherheit

- **WICHTIG:** API-Key niemals committen!
- Code-Generierung ist öffentlich
- Keine sensiblen Daten in Prompts

---
*Code-Generierung für OpenClaw* 💻
