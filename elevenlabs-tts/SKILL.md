---
name: elevenlabs-tts
description: Generate high-quality Text-to-Speech audio using ElevenLabs API with custom cloned voices. Use when the user wants to create voice messages, text-to-speech output, or audio files from text. Primary TTS solution with Piper TTS as fallback only when ElevenLabs is unavailable or credits exhausted. Supports German and 70+ languages via eleven_multilingual_v2 model.
---

# ElevenLabs TTS

**Status:** ✅ Active since 17.04.2026

Primary Text-to-Speech solution using ElevenLabs API with custom Drachenlord voice clone.

## Quick Start

```bash
# Generate speech with default settings (Drachenlord voice)
python3 scripts/elevenlabs_tts.py speak "Hallo Kosta, ich bin der Drachenlord!"

# Custom voice and model
python3 scripts/elevenlabs_tts.py speak "Text hier" --voice VOICE_ID --model MODEL_ID
```

## Configuration

**Required in `.env`:**
```bash
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Active Voice:**
- **voice_id:** `NkhHdPbLqYzmdIaSUuIy` (Drachenlord clone)

## Models & Credits

| Model | Credits | Use Case |
|-------|---------|----------|
| `eleven_multilingual_v2` | Standard | **Default** - Best quality, 70+ languages |
| `eleven_flash_v2.5` | Low | Fastest latency |
| `eleven_turbo_v2.5` | Low | Real-time applications |

## Usage Patterns

### 1. Standard Voice Message (Drachenlord)
```python
# For Butler-style messages to Kosta
python3 scripts/elevenlabs_tts.py speak \
  "Hallo Kosta, ich bin der Drachenlord. Ab sofort bin ich der Butler vom Freibeuter." \
  --voice NkhHdPbLqYzmdIaSUuIy \
  --model eleven_multilingual_v2
```

### 2. Send as Telegram Voice Message
```python
# Generate and send
python3 scripts/elevenlabs_tts.py speak "Nachricht"
# Then use filePath in message(action='send', asVoice=True, filePath='/tmp/elevenlabs_output.mp3')
```

## TTS Priority Rules

**CRITICAL - Hierachy:**

1. ✅ **ElevenLabs** (Primary) - Use for ALL TTS unless unavailable
2. ✅ **Piper TTS** (Fallback ONLY) - Use ONLY when:
   - ElevenLabs API is down
   - Credits exhausted
   - API errors persist
3. ❌ **NEVER gTTS** - Decommissioned, forbidden by user

**When to use Piper (Fallback):**
```python
# If ElevenLabs fails with credits or API errors
python3 scripts/piper_tts_fixed.py "Nachricht"
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `402 Payment Required` | Credits exhausted | Add credits or use Piper fallback |
| `401 Unauthorized` | API key invalid/berechtigung missing | Check API key and permissions |
| `404 Voice Not Found` | Wrong voice_id | Use correct voice_id from dashboard |
| `400 Bad Request` | Invalid model_id | Use `eleven_multilingual_v2` |

## Voice Settings

Default settings used:
```json
{
  "stability": 0.5,
  "similarity_boost": 0.75,
  "style": 0.0,
  "use_speaker_boost": true
}
```

## Files

- **Script:** `scripts/elevenlabs_tts.py`
- **Output:** `/tmp/elevenlabs_output.mp3` (default)
- **Workspace copy:** For Telegram voice messages

## IMPORTANT NOTES

- **Free Tier:** Does NOT exist anymore for API usage (changed 2025/2026)
- **Credits required:** All API calls consume credits
- **Voice Library vs Custom:** Library voices require paid plan, custom clones work with credits
- **German support:** ✅ Full support via multilingual_v2 model

## Changelog

- **17.04.2026:** Activated as primary TTS, Drachenlord voice configured
- **17.04.2026:** Piper demoted to fallback-only status
- **17.04.2026:** gTTS officially forbidden
