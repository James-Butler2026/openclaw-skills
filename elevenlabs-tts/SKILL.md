---
name: elevenlabs-tts
description: Generate high-quality Text-to-Speech audio using ElevenLabs API with custom cloned voices. OPTIMIZED with retry logic, logging, and proper argument parsing.
version: 2.0
---

# ElevenLabs TTS v2.0

**Status:** ✅ Active since 17.04.2026 | **Optimized:** 21.04.2026

Primäre TTS-Lösung für OpenClaw mit individuell geklonten Stimmen.

## ✅ Optimizations in v2.0

- 🔄 **Retry Logic** - Automatic retries on API failures
- 📝 **Logging** - Proper logging instead of print()
- ⚙️ **Argparse** - Better CLI with --help and subcommands
- 🛡️ **Error Handling** - Improved error messages and handling
- 📊 **Statistics** - Automatic cost tracking

## Quick Start

```bash
# Generate speech with default settings (Drachenlord voice)
python3 scripts/elevenlabs_tts.py speak "Hallo Kosta, ich bin der Drachenlord!"

# Custom voice and model
python3 scripts/elevenlabs_tts.py speak "Text hier" --voice VOICE_ID --model MODEL_ID

# List available voices
python3 scripts/elevenlabs_tts.py list

# List German voices
python3 scripts/elevenlabs_tts.py list-de

# List available models
python3 scripts/elevenlabs_tts.py models

# Get help
python3 scripts/elevenlabs_tts.py --help
python3 scripts/elevenlabs_tts.py speak --help
```

## Configuration

**Required in `.env`:**
```bash
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Optional config file:** `config/config.json`
```json
{
  "default_voice": "NkhHdPbLqYzmdIaSUuIy",
  "default_model": "eleven_multilingual_v2",
  "retry_attempts": 3,
  "cost_per_1000_chars": 0.267
}
```

**Active Voice:**
- **voice_id:** `NkhHdPbLqYzmdIaSUuIy` (Drachenlord geklonte Stimme)

## Models & Credits

| Model | Credits | Use Case |
|-------|---------|----------|
| `eleven_multilingual_v2` | Standard | **Default** - Best quality, 70+ languages |
| `eleven_flash_v2.5` | Low | Fastest latency |
| `eleven_turbo_v2.5` | Low | Real-time applications |

## NEW RULE (17.04.2026):

> When sending voice messages: Report character count + total + duration!
> Format: `[XXX chars | Total: YYYY | ZZ.Zs]`
>
> **STANDARD:** Bei jeder Drachenlord-Sprachnachricht wird die Statistik AUTOMATISCH unter die Nachricht angehängt!
> ```
> 🐉 Der Drachenlord sagt: ...
>
> [243 Zeichen | Total: 8672 | 2.32€ | 16.2s]
> ```

## Usage Examples

```bash
# Standard Voice Message (Drachenlord)
python3 scripts/elevenlabs_tts.py speak \
  "Hallo Kosta, ich bin der Drachenlord. Ab sofort bin ich der Butler vom Freibeuter."

# Custom voice
python3 scripts/elevenlabs_tts.py speak "Nachricht" --voice VOICE_ID

# Custom model
python3 scripts/elevenlabs_tts.py speak "Nachricht" --model eleven_flash_v2.5

# Custom output path
python3 scripts/elevenlabs_tts.py speak "Nachricht" --output /path/to/output.mp3
```

## Voice Settings

Empfohlene Voice Settings (hardcoded in script):
```json
{
  "stability": 1.0,
  "similarity_boost": 0.9,
  "style": 0.1,
  "use_speaker_boost": true,
  "speed": 0.8
}
```

**Warum diese Settings:**
- `speed: 0.8` - Etwas flotter als vorher (0.7), bessere Verständlichkeit
- `stability: 1.0` - Maximum! Konsistente Stimme
- `similarity_boost: 0.9` - Hohe Ähnlichkeit zum Original
- `style: 0.1` - Wenig Stil-Variation
- `use_speaker_boost: true` - Klarere Aussprache

## Error Handling (NEW in v2.0)

| Error | Cause | Solution |
|-------|-------|----------|
| `402 Payment Required` | Credits exhausted | Add credits |
| `401 Unauthorized` | API key invalid | Check API key |
| `404 Voice Not Found` | Wrong voice_id | Use correct voice_id |
| `400 Bad Request` | Invalid model_id | Use `eleven_multilingual_v2` |
| `5xx Server Error` | ElevenLabs down | **Automatic retry (3x)** |
| `Timeout` | Slow connection | **Automatic retry (3x)** |

## Statistics Tracking

Automatic cost tracking in `data/elevenlabs_stats.json`:
```json
{
  "total_chars": 8672,
  "total_cost_eur": 2.32
}
```

**Cost calculation:** 1000 characters = 0.267€

## Changelog

- **21.04.2026 (v2.0):** Retry logic, logging, argparse, improved error handling
- **18.04.2026:** Speed increased from 0.7 to 0.8
- **17.04.2026:** Activated as primary TTS, Drachenlord voice configured
- **17.04.2026:** Piper demoted to fallback-only status
