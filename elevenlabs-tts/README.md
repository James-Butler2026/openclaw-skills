# ElevenLabs TTS Skill

🐉 **Der Drachenlord spricht!** - Premium Text-to-Speech mit custom cloned voice.

## Überblick

Dieser Skill integriert die ElevenLabs API als **primäre TTS-Lösung** für James. Die charakteristische Drachenlord-Stimme bringt eine einzigartige Note in alle Sprachnachrichten.

**Status:** Primary TTS (seit 17.04.2026)  
**Fallback:** Piper TTS (nur bei API-Ausfall)  
**Verboten:** gTTS (decommissioned)

## Features

- 🎙️ **Drachenlord Voice Clone** - Einzigartige Stimme
- 🌍 **70+ Sprachen** via eleven_multilingual_v2
- ⚡ **Low Latency** Modelle verfügbar
- 🔄 **Intelligentes Fallback** zu Piper bei Problemen

## Installation

```bash
# Abhängigkeiten (bereits im Docker-Setup)
pip install requests python-dotenv
```

## Konfiguration

**`.env` eintragen:**
```bash
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Voice ID:** `NkhHdPbLqYzmdIaSUuIy` (Drachenlord)

## Verwendung

### Kommandozeile

```bash
# Sprachnachricht generieren
python3 scripts/elevenlabs_tts.py speak "Hallo Kosta, ich bin der Drachenlord!"

# Als Telegram Voice senden
python3 scripts/elevenlabs_tts.py speak "Nachricht" --output /tmp/drache.mp3
```

### In Python

```python
from scripts.elevenlabs_tts import generate_speech

# Generieren
audio_path = generate_speech(
    text="Grüße vom Drachenlord!",
    voice_id="NkhHdPbLqYzmdIaSUuIy",
    model_id="eleven_multilingual_v2"
)

# Senden
message(action='send', asVoice=True, filePath=audio_path)
```

## Modelle

| Modell | Credits | Verwendung |
|--------|---------|------------|
| `eleven_multilingual_v2` | Standard | **Default** - Beste Qualität |
| `eleven_flash_v2.5` | Low | Schnellste Antwortzeit |
| `eleven_turbo_v2.5` | Low | Echtzeit-Anwendungen |

## TTS Priorität

```
1. ElevenLabs (Drachenlord) ✅ PRIMARY
   ↓ (bei Fehler)
2. Piper TTS (Thorsten) ✅ FALLBACK
   ↓ (nie!)
3. gTTS ❌ VERBOTEN
```

## Fehlerbehandlung

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| `402` | Credits aufgebraucht | Piper Fallback |
| `401` | API Key ungültig | `.env` prüfen |
| `404` | Voice ID falsch | Dashboard prüfen |

## Dateien

- `SKILL.md` - Vollständige Dokumentation
- `scripts/elevenlabs_tts.py` - Hauptscript
- `README.md` - Diese Datei

## Changelog

- **17.04.2026:** Aktiviert als Primary TTS
- **17.04.2026:** Drachenlord Voice konfiguriert
- **17.04.2026:** Piper zu Fallback degradiert

---

*Rainer Winkler würde stolz sein* 🐉🎩
