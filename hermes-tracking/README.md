# hermes-tracking

OpenClaw Skill: Hermes Tracking

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/{USERNAME}/openclaw-skills.git
cd openclaw-skills/hermes-tracking
```

### 2. Abhängigkeiten installieren

```bash
pip install playwright pytesseract Pillow
playwright install chromium
```

System-Abhängigkeiten:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu
```

## Nutzung

```bash
python3 scripts/hermes_tracker.py H1003660401590901036
```

## 📖 Dokumentation

Siehe [SKILL.md](SKILL.md) für vollständige Dokumentation.

---

*Part of OpenClaw Skills Collection*
