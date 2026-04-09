---
name: audio-transcription
description: Transcribe audio files (MP3, OGG, WAV, etc.) to text using faster-whisper. Use when the user needs to convert voice messages, audio recordings, podcasts, or any audio content into written text. Supports multiple languages (auto-detection or specified), various Whisper models (tiny to large-v3), and common audio formats.
---

# Audio Transcription

Transcribe audio files to text using OpenAI's Whisper (via faster-whisper).

## Quick Start

Use the included script to transcribe any audio file:

```bash
python3 scripts/transcribe.py <audio-file> [--language de] [--model small]
```

### Examples

```bash
# Auto-detect language (recommended)
python3 scripts/transcribe.py sprachnachricht.ogg

# Specify German language explicitly
python3 scripts/transcribe.py audio.mp3 --language de

# Use a faster model (less accurate)
python3 scripts/transcribe.py audio.mp3 --model tiny

# Use best quality model (slower)
python3 scripts/transcribe.py audio.mp3 --model large-v3 --language de
```

## Available Models

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `tiny` | Fastest | Basic | Quick drafts, noisy audio |
| `base` | Fast | Good | Balanced for short clips |
| `small` | Medium | Better | **Default** - good balance |
| `medium` | Slower | Very good | Clear audio, important content |
| `large-v3` | Slowest | Best | Critical content, maximum accuracy |

## Supported Languages

Auto-detection works well for most languages. Specify explicitly with `--language`:
- `de` - German
- `en` - English
- `es` - Spanish
- `fr` - French
- `it` - Italian
- `nl` - Dutch
- `pt` - Portuguese
- And many more...

## Requirements

- Python 3.8+
- faster-whisper installed in `/home/node/.openclaw/venv`

Install dependencies if needed:
```bash
python3 -m venv /home/node/.openclaw/venv
/home/node/.openclaw/venv/bin/pip install faster-whisper
```

## Scripts

### `scripts/transcribe.py`

Main transcription script with arguments:
- `audio_file` (required) - Path to audio file
- `--language`, `-l` - Language code (default: auto)
- `--model`, `-m` - Model size (default: small)

Returns: Transcribed text printed to stdout
