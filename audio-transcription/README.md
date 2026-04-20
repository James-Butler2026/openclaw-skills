# Audio Transcription Skill

Transkribiere Audio-Dateien (MP3, OGG, WAV, etc.) zu Text mit faster-whisper.

## Features

- 🎙️ Unterstützt MP3, OGG, WAV, etc.
- 🤖 Mehrere Whisper-Modelle: tiny bis large-v3
- 🌍 Auto-Detect Sprache oder explizit angeben
- 🇩🇪 Deutsche Sprache nativ unterstützt

## Installation

```bash
# Skill-Ordner verwenden
cd ~/.openclaw/workspace/skills/audio-transcription/

# Abhängigkeiten (falls nötig)
# faster-whisper ist im OpenClaw venv vorinstalliert
```

## Verwendung

```bash
# Auto-detect Sprache
python3 scripts/transcribe.py sprachnachricht.ogg

# Deutsch explizit
python3 scripts/transcribe.py audio.mp3 --language de

# Schnelles Modell
python3 scripts/transcribe.py audio.mp3 --model tiny
```

## Verfügbare Modelle

| Modell | Geschwindigkeit | Qualität |
|--------|----------------|----------|
| tiny | Schnellste | Basic |
| base | Schnell | Gut |
| small | Mittel | Besser |
| medium | Langsamer | Sehr gut |
| large-v3 | Langsamste | Beste |

## Konfiguration

Keine zusätzliche Konfiguration nötig – nutzt faster-whisper aus dem OpenClaw venv.

## Sicherheit

- Audio-Dateien werden verarbeitet und können gelöscht werden
- Keine Daten werden an externe Server gesendet (lokale Verarbeitung)

---
*Lokale Audio-Transkription für OpenClaw* 🎙️
