# audio-transcription

OpenClaw Skill: Audio Transcription

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/{USERNAME}/openclaw-skills.git
cd openclaw-skills/audio-transcription
```

### 2. Abhängigkeiten installieren

```bash
pip install faster-whisper
```

Optional: Für GPU-Beschleunigung:
```bash
pip install torch torchvision torchaudio
```

## Nutzung

```bash
python3 scripts/transcribe.py audio.mp3 --language de
```

## 📖 Dokumentation

Siehe [SKILL.md](SKILL.md) für vollständige Dokumentation.

---

*Part of OpenClaw Skills Collection*
