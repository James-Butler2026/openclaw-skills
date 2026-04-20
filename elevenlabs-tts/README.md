# ElevenLabs TTS Skill

Hochwertige Text-to-Speech mit ElevenLabs API und benutzerdefinierten Stimmen.

## Features

- 🎙️ Hochwertige Sprachausgabe
- 🌍 Mehrere Sprachen unterstützt
- 🎭 Benutzerdefinierte Stimmen möglich
- ⚡ Schnelle Generierung

## Installation

```bash
cd ~/.openclaw/workspace/skills/elevenlabs-tts/
```

## Verwendung

```bash
# Sprache generieren
python3 scripts/elevenlabs_tts.py speak "Hallo Welt"

# Mit eigener Voice ID
python3 scripts/elevenlabs_tts.py speak "Text" --voice YOUR_VOICE_ID

# Mit Modell-Auswahl
python3 scripts/elevenlabs_tts.py speak "Text" --model eleven_multilingual_v2
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Voice ID konfigurieren:**
Bearbeite `scripts/elevenlabs_tts.py` und setze deine Voice ID:
```python
DEFAULT_VOICE = "YOUR_VOICE_ID_HERE"
```

## Sicherheit

- **NIE** Voice IDs in öffentliche Repos committen
- **NIE** API-Keys in Code schreiben
- `.env` Datei ist in `.gitignore` eingetragen

---
*Premium Text-to-Speech für OpenClaw* 🎙️
