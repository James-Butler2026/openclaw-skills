# Image Generation Skill

Kostenlose Bildgenerierung via Pollinations.ai API.

## Features

- 🎨 Kein API-Key nötig
- 🆓 Keine Rate-Limits bekannt
- 📐 Custom Dimensionen und Seeds
- 🚫 Watermark-freier Output

## Schnellstart

```bash
# Einfaches Bild
python3 scripts/generate_image.py "A beautiful sunset over mountains"

# Mit benutzerdefinierten Dimensionen
python3 scripts/generate_image.py "Cyberpunk city" --width 1024 --height 768

# Mit spezifischem Seed (Reproduzierbarkeit)
python3 scripts/generate_image.py "Portrait of a cat" --seed 123

# Ausgabe in bestimmte Datei
python3 scripts/generate_image.py "Abstract art" --output myart.png
```

## Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `prompt` | (required) | Bildbeschreibung |
| `--width` | 512 | Bildbreite in Pixeln |
| `--height` | 512 | Bildhöhe in Pixeln |
| `--seed` | 42 | Seed für Reproduzierbarkeit |
| `--output` | auto | Ausgabedatei |

## API-Endpunkt

```
https://image.pollinations.ai/prompt/{URL_ENCODED_PROMPT}?width={W}&height={H}&seed={S}&nologo=true
```

## Python API

```python
from scripts.generate_image import generate_image

result = generate_image(
    prompt="A beautiful landscape",
    width=1024,
    height=768,
    seed=42,
    output="/path/to/image.png"
)
print(f"Bild gespeichert: {result}")
```

## Einschränkungen

- **Qualität:** Nicht ganz DALL-E 3 Niveau, aber sehr brauchbar
- **Kommerzielle Nutzung:** Prüfen vor kommerziellem Einsatz
- **Rate Limits:** Keine bekannt, aber fair use beachten

## Vergleich mit Alternativen

| Service | Kosten | API-Key | Qualität |
|---------|--------|---------|----------|
| **Pollinations.ai** | Kostenlos | Nein | Gut |
| DALL-E 3 | Bezahlt | Ja | Exzellent |
| Midjourney | Bezahlt | Ja | Exzellent |
| Leonardo.ai | Freemium | Ja | Gut |

---

*Teil der OpenClaw Skills Collection* 🎩
