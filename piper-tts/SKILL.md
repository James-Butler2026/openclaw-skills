---
name: piper-tts
description: German Text-to-Speech using Piper TTS with Thorsten voice. Generate audio files from text, play directly, or send as voice messages. No API keys needed - runs locally with high quality German voice synthesis.
---

# Piper TTS Skill

Deutsche Text-to-Speech mit der Thorsten-Stimme. Lokal auf dem Server, keine API-Keys, keine Kosten!

## Features

- 🎙️ **Lokale Sprachsynthese** – Kein Internet nötig
- 🇩🇪 **Deutsch (Thorsten)** – Natürliche männliche Stimme
- 💾 **Audio-Dateien** – WAV für weitere Verwendung
- 🔊 **Direktes Abspielen** – Sofort anhören
- 📱 **Voice-Messages** – Als Telegram-Sprachnachricht senden

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/James-Butler2026/openclaw-skills.git
cd openclaw-skills/piper-tts
```

### 2. Piper TTS installieren

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install piper-tts

# Oder via pip
pip install piper-tts

# Stimmen-Download (Thorsten, Deutsch)
mkdir -p ~/.local/share/piper-tts
cd ~/.local/share/piper-tts
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE-thorsten-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE-thorsten-medium.onnx.json
```

### 3. Python-Abhängigkeiten

```bash
pip install pyTelegramBotAPI
```

### 4. Konfiguration

Erstelle eine `.env` Datei:

```bash
# Optional: Pfade konfigurieren
PIPER_MODEL_PATH=~/.local/share/piper-tts/
```

## Schnellstart

### Text zu Audio-Datei
```bash
# Einfache Sprachnachricht
python3 scripts/piper_tts.py "Hallo Welt"

# Ausgabe in bestimmte Datei
python3 scripts/piper_tts.py "Guten Morgen" -o ~/morgen.wav

# Mit Text aus Datei
python3 scripts/piper_tts.py -f nachricht.txt
```

### Direkt abspielen
```bash
# Erzeugen UND sofort abspielen
python3 scripts/piper_tts.py "Das ist ein Test" --play

# Kurzform
python3 scripts/piper_tts.py "Hallo" -p
```

### Als Telegram-Voice senden
```bash
# An Standard-Chat
python3 scripts/piper_tts.py "Ihre Nachricht ist angekommen" --send

# Kurzform
python3 scripts/piper_tts.py "Erinnerung: Termin um 15 Uhr" -s
```

## Parameter

| Parameter | Kurzform | Beschreibung |
|-----------|----------|--------------|
| `text` | - | Text zu sprechen (in Anführungszeichen) |
| `--file` | `-f` | Text aus Datei laden |
| `--output` | `-o` | Ausgabedatei (Default: /tmp/piper_output.wav) |
| `--play` | `-p` | Direkt abspielen nach Generierung |
| `--send` | `-s` | Als Telegram-Voice senden |
| `--speed` | - | Sprechgeschwindigkeit (0.5-2.0, Default: 1.0) |

## Python API

```python
from scripts.piper_tts import generate_speech, play_audio, send_voice

# Nur generieren
audio_path = generate_speech("Hallo Welt")
print(f"Audio: {audio_path}")

# Generieren und abspielen
audio_path = generate_speech("Guten Tag", play=True)

# Generieren und als Voice senden
audio_path = generate_speech("Ihre Nachricht", send_voice=True)
```

## Technische Details

- **Modell:** Thorsten (medium)
- **Sprache:** Deutsch (de_DE)
- **Auflösung:** 22050 Hz
- **Format:** WAV PCM 16-bit

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| "piper: command not found" | `pip install piper-tts` oder `apt-get install piper-tts` |
| Kein Sound | Lautstärke prüfen (`alsamixer`) |
| "Voice send failed" | Telegram Token prüfen, Chat-ID prüfen |

---

*Piper TTS – Lokale, kostenlose deutsche Sprachsynthese!* 🎙️🎩
