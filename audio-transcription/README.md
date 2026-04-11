# Audio Transcription Skill

Audio zu Text Transkription mit faster-whisper (OpenAI Whisper).

## Features

- 🎙️ Transkribiert MP3, OGG, WAV, etc.
- 🤖 Verschiedene Modelle: tiny bis large-v3
- 🌍 Auto-Detect Sprache oder explizit angeben
- 🇩🇪 Deutsche Sprache nativ unterstützt

## Schnellstart

```bash
# Auto-detect Sprache (empfohlen)
python3 scripts/transcribe.py sprachnachricht.ogg

# Deutsch explizit
python3 scripts/transcribe.py audio.mp3 --language de

# Schnelleres Modell
python3 scripts/transcribe.py audio.mp3 --model tiny

# Beste Qualität
python3 scripts/transcribe.py audio.mp3 --model large-v3
```

## Modelle

| Modell | Geschwindigkeit | Qualität | Einsatzgebiet |
|--------|----------------|----------|---------------|
| `tiny` | Schnellsten | Basis | Schnelle Entwürfe |
| `base` | Schnell | Gut | Balance für Kurzclips |
| `small` | Mittel | Besser | **Standard** - gute Balance |
| `medium` | Langsamer | Sehr gut | Klare Audio, wichtiger Inhalt |
| `large-v3` | Langsamste | Beste | Kritischer Inhalt, max. Genauigkeit |

## Konfiguration

Keine API-Keys nötig – läuft lokal mit faster-whisper!

```bash
# Installation
pip install faster-whisper
```

## Python API

```python
from scripts.transcribe import transcribe_audio

text = transcribe_audio("audio.mp3", language="de")
print(text)
```

---

*Teil der OpenClaw Skills Collection* 🎩
