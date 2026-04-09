# image-generation

---
name: image-generation
description: Kostenlose Bildgenerierung via Pollinations.ai API. Kein API-Key nötig. Use when the user wants to generate images, create AI art, or needs image generation without paid APIs like DALL-E or Midjourney. Supports custom dimensions, seeds for reproducibility, and watermark-free output.
---

# Image Generation Skill

Kostenlose Bildgenerierung via Pollinations.ai – keine Registrierung, kein API-Key, keine Rate-Limits bekannt.

## Schnellstart

```bash
# Einfaches Bild generieren
python3 skills/image-generation/scripts/generate_image.py "A beautiful sunset over mountains"

# Mit benutzerdefinierten Dimensionen
python3 skills/image-generation/scripts/generate_image.py "Cyberpunk city" --width 1024 --height 768

# Mit spezifischem Seed (für Reproduzierbarkeit)
python3 skills/image-generation/scripts/generate_image.py "Portrait of a cat" --seed 123

# Ausgabe in bestimmte Datei
python3 skills/image-generation/scripts/generate_image.py "Abstract art" --output myart.png
```

## Parameter

| Parameter | Kurzform | Default | Beschreibung |
|-----------|----------|---------|--------------|
| `prompt` | - | (required) | Bildbeschreibung (in Anführungszeichen) |
| `--width` | - | 512 | Bildbreite in Pixeln |
| `--height` | - | 512 | Bildhöhe in Pixeln |
| `--seed` | - | 42 | Seed für Reproduzierbarkeit |
| `--output` | `-o` | auto | Ausgabedatei (default: /tmp/{prompt}_seed{seed}.png) |
| `--logo` | - | false | Watermarkerlaubnis aktivieren |

## API-Endpunkt

```
https://image.pollinations.ai/prompt/{URL_ENCODED_PROMPT}?width={W}&height={H}&seed={S}&nologo=true
```

### Direkte API-Nutzung

```python
import urllib.parse
import urllib.request

prompt = "A digital art portrait of an elegant butler"
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&seed=42&nologo=true"

urllib.request.urlretrieve(url, "output.png")
```

## Verwendung in Python

```python
from skills.image_generation.scripts.generate_image import generate_image

# Einfacher Aufruf
result = generate_image("A beautiful landscape")
print(f"Bild gespeichert: {result}")

# Mit Optionen
result = generate_image(
    prompt="Cyberpunk city at night",
    width=1024,
    height=768,
    seed=123,
    output="/path/to/city.png"
)
```

## Einschränkungen

- **Qualität:** Nicht ganz DALL-E 3 Niveau, aber sehr brauchbar
- **Kommerzielle Nutzung:** Prüfen vor kommerziellem Einsatz
- **Rate Limits:** Keine bekannt, aber fair use beachten
- **NSFW:** Wird herausgefiltert

## Vergleich mit Alternativen

| Service | Kosten | API-Key | Qualität | Rate Limits |
|---------|--------|---------|----------|-------------|
| **Pollinations.ai** | Kostenlos | Nein | Gut | Unbekannt |
| DALL-E 3 | Bezahlt | Ja | Exzellent | Ja |
| Midjourney | Bezahlt | Ja | Exzellent | Ja |
| Leonardo.ai | Freemium | Ja | Gut | Tägliche Credits |
| Bing Image Creator | Kostenlos | Microsoft-Konto | Gut | 15 Boosts/Woche |

## Beispiele

```bash
# Butler-Portrait (wie erstellt am 09.04.2026)
python3 scripts/generate_image.py "A digital art portrait of an elegant butler named James in Victorian style black suit white shirt bow tie tall top hat friendly sophisticated expression digital art clean lines warm lighting professional character design" --width 512 --height 512 --seed 42

# Landschaft
python3 scripts/generate_image.py "A serene mountain lake at sunrise with misty peaks reflected in crystal clear water"

# Abstrakt
python3 scripts/generate_image.py "Abstract geometric patterns in blue and gold, modern art style"
```

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Timeout | Größere Dimensionen vermeiden oder `--width`/`--height` reduzieren |
| Fehler 404 | URL-Encoding prüfen (Sonderzeichen müssen encoded sein) |
| Leeres Bild | Prompt vereinfachen oder Seed ändern |

---

*Erstellt am 09.04.2026 für Eure Lordschaft* 🎩
