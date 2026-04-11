# Piper TTS Skill

Deutsche Text-to-Speech mit Thorsten-Stimme - lokal, keine API-Keys!

## Features

- 🎙️ **Lokale Sprachsynthese** - Kein Internet nötig
- 🇩🇪 **Deutsch (Thorsten)** - Natürliche männliche Stimme
- 💾 **Audio-Dateien** - WAV für Weiterverwendung
- 🔊 **Direktes Abspielen** - Sofort anhören
- 📱 **Voice-Messages** - Als Telegram-Sprachnachricht senden

## Schnellstart

```bash
# Einfache Sprachnachricht
python3 scripts/piper_tts.py "Hallo Welt"

# Ausgabe in bestimmte Datei
python3 scripts/piper_tts.py "Guten Morgen" -o ~/morgen.wav

# Erzeugen UND sofort abspielen
python3 scripts/piper_tts.py "Das ist ein Test" --play

# Als Telegram-Voice senden
python3 scripts/piper_tts.py "Ihre Nachricht ist angekommen" --send

# Text aus Datei
python3 scripts/piper_tts.py -f nachricht.txt
```

## Installation

```bash
# Piper TTS installieren
apt-get install piper-tts  # Debian/Ubuntu
# oder: pip install piper-tts

# Stimmen-Download (Thorsten, Deutsch)
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE-thorsten-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE-thorsten-medium.onnx.json
```

## Parameter

| Parameter | Beschreibung |
|-----------|--------------|
| `text` | Text zu sprechen |
| `--file` | Text aus Datei laden |
| `--output` | Ausgabedatei (Default: /tmp/piper_output.wav) |
| `--play` | Direkt abspielen |
| `--send` | Als Telegram-Voice senden |
| `--speed` | Sprechgeschwindigkeit (0.5-2.0) |

## Python API

```python
from scripts.piper_tts import generate_speech, play_audio, send_voice

# Nur generieren
audio_path = generate_speech("Hallo Welt")

# Generieren und abspielen
audio_path = generate_speech("Guten Tag", play=True)

# Generieren und senden
audio_path = generate_speech("Ihre Nachricht", send_voice=True)
```

## Technische Details

- **Modell:** Thorsten (medium)
- **Sprache:** Deutsch (de_DE)
- **Auflösung:** 22050 Hz
- **Format:** WAV PCM 16-bit

---

*Teil der OpenClaw Skills Collection* 🎩
