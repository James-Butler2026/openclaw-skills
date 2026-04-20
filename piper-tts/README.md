# Piper TTS Skill

Deutsche Text-to-Speech (lokal) mit Thorsten-Stimme – kein API-Key nötig!

## Features

- 🗣️ Thorsten-Stimme (deutsch, männlich)
- 🔒 Kein API-Key nötig
- 🏠 Lokale Ausführung
- 📱 Telegram Voice-Messages

## Installation

```bash
cd ~/.openclaw/workspace/skills/piper-tts/

# Piper muss installiert sein
# Siehe SYSTEM.md für Installationsanleitung
```

## Verwendung

```bash
# Text zu Sprache
python3 scripts/piper_tts.py "Hallo Welt"

# Als Telegram Voice-Message senden
python3 scripts/piper_tts.py "Hallo" --send

# Ausgabe in Datei
python3 scripts/piper_tts.py "Nachricht" --output /tmp/output.wav
```

## Konfiguration

Keine Konfiguration nötig – läuft lokal ohne Cloud.

## Sicherheit

- 100% offline – keine Internetverbindung nötig
- Keine Daten werden übertragen
- Datenschutzfreundlich

---
*Lokale Text-to-Speech für OpenClaw* 🗣️
