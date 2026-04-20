# Image Generation Skill

Kostenlose Bildgenerierung via Pollinations.ai – kein API-Key nötig!

## Features

- 🎨 Kein API-Key nötig
- 🚀 Keine Rate-Limits bekannt
- 📐 Custom Dimensionen und Seeds
- 🚫 Watermark-freier Output

## Installation

```bash
cd ~/.openclaw/workspace/skills/image-generation/
```

## Verwendung

```bash
# Bild generieren
python3 scripts/generate_image.py "A beautiful sunset"

# Mit Dimensionen
python3 scripts/generate_image.py "Ein elegantes Maskottchen" \
    --width 1024 --height 768

# Mit Seed (reproduzierbar)
python3 scripts/generate_image.py "Landschaft" --seed 42

# Speichern
python3 scripts/generate_image.py "Portrait" --output portrait.png
```

## Konfiguration

Keine Konfiguration nötig – Pollinations.ai ist kostenlos.

## Sicherheit

- Keine Registrierung nötig
- Keine persönlichen Daten erforderlich
- Bilder sind öffentlich generierbar

---
*Kostenlose Bildgenerierung für OpenClaw* 🎨
