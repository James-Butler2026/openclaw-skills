# piper-tts

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

## Voraussetzungen

Piper TTS ist bereits installiert auf dem Server:
- **Pfad:** `/usr/local/bin/piper`
- **Stimme:** `/usr/local/share/piper-voices/de_DE-thorsten-medium.onnx`
- **Format:** WAV (44.1kHz, 16-bit)

## Schnellstart

### Text zu Audio-Datei
```bash
# Einfache Sprachnachricht
python3 skills/piper-tts/scripts/piper_tts.py "Hallo Welt"

# Ausgabe in bestimmte Datei
python3 skills/piper-tts/scripts/piper_tts.py "Guten Morgen" -o ~/morgen.wav

# Mit Text aus Datei
python3 skills/piper-tts/scripts/piper_tts.py -f nachricht.txt
```

### Direkt abspielen
```bash
# Erzeugen UND sofort abspielen
python3 skills/piper-tts/scripts/piper_tts.py "Das ist ein Test" --play

# Kurzform
python3 skills/piper-tts/scripts/piper_tts.py "Hallo" -p
```

### Als Telegram-Voice senden
```bash
# An Standard-Chat (Eure Lordschaft)
python3 skills/piper-tts/scripts/piper_tts.py "Ihre Nachricht ist angekommen" --send

# Kurzform
python3 skills/piper-tts/scripts/piper_tts.py "Erinnerung: Termin um 15 Uhr" -s
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
| `--speaker` | - | Sprecher-ID (falls mehrere Stimmen) |

## Python API

```python
from skills.piper_tts.scripts.piper_tts import generate_speech, play_audio, send_voice

# Nur generieren
audio_path = generate_speech("Hallo Welt")
print(f"Audio: {audio_path}")

# Generieren und abspielen
audio_path = generate_speech("Guten Tag", play=True)

# Generieren und als Voice senden
audio_path = generate_speech("Ihre Nachricht", send_voice=True)

# Mit Optionen
audio_path = generate_speech(
    text="Dies ist ein längerer Text",
    output_path="/tmp/custom.wav",
    speed=1.2
)
```

## Beispiele

### Morgenansage
```bash
python3 skills/piper-tts/scripts/piper_tts.py \
    "Guten Morgen! Es ist 7 Uhr. Das Wetter ist sonnig." \
    --play
```

### Erinnerung
```bash
python3 skills/piper-tts/scripts/piper_tts.py \
    "Erinnerung: Arzttermin bei Dr. Kaufmann um 16 Uhr 30" \
    --send
```

### Aus Datei
```bash
# Erstelle Textdatei
echo "Ihre tägliche Zusammenfassung ist fertig" > /tmp/nachricht.txt

# Zu Sprache machen
python3 skills/piper-tts/scripts/piper_tts.py \
    -f /tmp/nachricht.txt \
    -o ~/nachricht.wav \
    --play
```

### In Scripts verwenden
```bash
#!/bin/bash
# Im Cron-Job für Erinnerungen

python3 skills/piper-tts/scripts/piper_tts.py \
    "Es ist Zeit für die tägliche Übung" \
    --send
```

## Technische Details

### Piper TTS Einstellungen
- **Modell:** Thorsten (medium)
- **Sprache:** Deutsch (de_DE)
- **Auflösung:** 22050 Hz
- **Format:** WAV PCM 16-bit
- **Geschwindigkeit:** Anpassbar (0.5x - 2.0x)

### Dateigröße
| Textlänge | Geschätzte Größe |
|-----------|------------------|
| Kurz (10 Wörter) | ~50-100 KB |
| Mittel (50 Wörter) | ~200-300 KB |
| Lang (200 Wörter) | ~800 KB - 1 MB |

### Einschränkungen
- Nur **Deutsch** unterstützt (Thorsten-Stimme)
- Keine anderen Sprachen verfügbar (ohne weitere Modelle)
- SSML/Markup nicht unterstützt (nur reiner Text)
- Sehr lange Texte (>500 Wörter) können langsam sein

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| "piper: command not found" | Piper ist installiert unter `/usr/local/bin/piper` |
| Kein Sound | Lautstärke prüfen (`alsamixer`), Lautsprecher verbunden? |
| "Voice send failed" | Telegram Token prüfen, Chat-ID prüfen |
| Zu langsam | `--speed 1.2` für schnelleres Sprechen |
| Roboter-Stimme | Normal bei Thorsten medium – ist qualitativ hochwertig |

## Vergleich mit Online-TTS

| Feature | Piper (lokal) | Google TTS | ElevenLabs |
|---------|--------------|------------|------------|
| Kosten | ✅ Kostenlos | ⚠️ Limitiert | ❌ Bezahlt |
| Internet | ❌ Nicht nötig | ✅ Nötig | ✅ Nötig |
| Latenz | ⭐⭐⭐ Sehr gering | ⭐⭐ Mittel | ⭐⭐⭐ Sehr gering |
| Qualität | ⭐⭐⭐ Gut | ⭐⭐⭐⭐ Sehr gut | ⭐⭐⭐⭐⭐ Exzellent |
| Datenschutz | ✅ Lokal | ❌ Cloud | ❌ Cloud |

---

*Piper TTS – Lokale, kostenlose deutsche Sprachsynthese für Eure Lordschaft!* 🎙️🎩
