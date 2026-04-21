---
name: audio-transcription
description: Transcribe audio files (MP3, OGG, WAV, etc.) to text using faster-whisper. OPTIMIZED with Int8-Quantization, model caching, VAD filtering, timestamps, progress display, and confidence scores for 3-5x faster transcription on CPU.
version: 2.1
---

# Audio Transcription v2.1 - OPTIMIZED

Transcribe audio files to text using OpenAI's Whisper (via faster-whisper) - **now 3-5x faster** through model caching and Int8-Quantization. **v2.1 adds timestamps, progress display, output files, and confidence scores!**

## ✅ New in v2.1

- 🕐 **Timestamps** - Segment timestamps [MM:SS] or [HH:MM:SS]
- 📄 **Output File** - Save transcription to .txt file
- 📊 **Progress Display** - See transcription progress in real-time
- 🎯 **Confidence Scores** - Quality indicators for each segment
- ✅ **Audio Format Validation** - Prevents crashes with invalid files
- 📁 **Batch Processing** - Multiple files with auto-save to directory

## Quick Start

### Single File
```bash
python3 skills/audio-transcription/scripts/transcribe.py sprachnachricht.ogg
```

### With Timestamps and Save
```bash
python3 skills/audio-transcription/scripts/transcribe.py podcast.mp3 --timestamps --output transcript.txt
```

### Batch Processing with Auto-Save
```bash
python3 skills/audio-transcription/scripts/transcribe.py *.ogg --output-dir ./transcripts/
```

## Available Models

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `tiny` | ⚡ Fastest | Basic | Quick drafts, noisy audio |
| `base` | ⚡⚡ Fast | Good | Balanced for short clips |
| `small` | ⚡⚡⚡ Medium | Better | Good balance |
| `medium` | 🐢 Slower | Very good | **Default** - clear audio |
| `large-v3` | 🐢🐢 Slowest | Best | Critical content, maximum accuracy |

## Compute Types

| Type | Speed | Quality | Recommended For |
|------|-------|---------|-----------------|
| `int8` | 🚀 **Fastest** | Good | **CPU (Default)** |
| `int16` | Fast | Better | CPU |
| `float16` | Medium | Very Good | GPU |
| `float32` | Slow | Best | GPU, maximum precision |

## Speed Comparison

**v1.0 (before):**
- First run: 45-60 seconds (model loading)
- Each run: 45-60 seconds

**v2.0 (optimized):**
- First run: 30-40 seconds (model loading + caching)
- Each subsequent run: **10-15 seconds** ⚡

**v2.1 (with progress display):**
- Shows real-time progress: `50% | ETA: 45s`
- More user-friendly for long files

## Usage Examples

```bash
# Auto-detect language, optimized for CPU (int8), default model (medium)
python3 skills/audio-transcription/scripts/transcribe.py sprachnachricht.ogg

# German language, with timestamps, save to file
python3 skills/audio-transcription/scripts/transcribe.py audio.mp3 \
  --language de --timestamps --output result.txt

# Batch processing - process all ogg files, auto-save to directory
python3 skills/audio-transcription/scripts/transcribe.py *.ogg --output-dir ./transcripts/

# Best quality with confidence scores (slower)
python3 skills/audio-transcription/scripts/transcribe.py podcast.mp3 \
  --model large-v3 --timestamps --confidence

# Clear model cache (if needed)
python3 skills/audio-transcription/scripts/transcribe.py audio.ogg --clear-cache
```

## Output Format

### Without Timestamps
```
Hallo und willkommen zum Podcast. Heute sprechen wir über KI...
```

### With Timestamps
```
[00:05] Hallo und willkommen zum Podcast.
[00:12] Heute sprechen wir über KI.
[00:18] (confidence: 0.97)
```

### With Timestamps + Confidence
```
[00:05] Hallo und willkommen zum Podcast. (confidence: 0.95)
[00:12] Heute sprechen wir über KI. (confidence: 0.97)
[00:18] Das Thema ist sehr spannend. (confidence: 0.92)
```

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
- ffprobe (optional, for audio duration detection)

Install dependencies if needed:
```bash
python3 -m venv /home/node/.openclaw/venv
/home/node/.openclaw/venv/bin/pip install faster-whisper
```

## Scripts

### `scripts/transcribe.py`

Main transcription script with optimized arguments:
- `audio_files` (required) - One or more audio files
- `--language`, `-l` - Language code (default: auto)
- `--model`, `-m` - Model size (default: medium)
- `--compute-type` - Int8, int16, float16, float32 (default: int8)
- `--output`, `-o` - Save transcription to file
- `--output-dir` - Save multiple transcriptions to directory
- `--timestamps`, `-t` - Add timestamps to output
- `--confidence`, `-c` - Show confidence scores
- `--no-progress` - Disable progress display
- `--clear-cache` - Clear model cache

## Changelog

### v2.1
- ✅ Timestamps (MM:SS, HH:MM:SS)
- ✅ Output file support (--output, --output-dir)
- ✅ Progress display with ETA
- ✅ Confidence scores
- ✅ Audio format validation
- ✅ Batch processing improvements

### v2.0
- ✅ Int8-Quantization (3x faster)
- ✅ Model caching
- ✅ VAD filtering
- ✅ Multi-CPU support

### v1.0
- Initial version

---
*Optimized for VPS deployment - no GPU required* 🚀
