# piper-tts

OpenClaw Skill: Piper Tts

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/{USERNAME}/openclaw-skills.git
cd openclaw-skills/piper-tts
```

### 2. Abhängigkeiten installieren

Piper muss auf dem System installiert sein:

```bash
# Ubuntu/Debian
sudo apt-get install piper-tts

# Oder aus dem Piper Repository
pip install piper-tts
```

### 3. Konfiguration

Erstelle eine `.env` Datei:

```bash
# Optional: Pfade konfigurieren
PIPER_MODEL_PATH=/usr/local/share/piper-voices/
```

## Nutzung

```bash
python3 scripts/piper_tts.py "Hallo Welt"
```

## 📖 Dokumentation

Siehe [SKILL.md](SKILL.md) für vollständige Dokumentation.

---

*Part of OpenClaw Skills Collection*
