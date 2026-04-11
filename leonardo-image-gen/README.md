# Leonardo AI Image Generation Skill

Bildgenerierung mit Leonardo AI API und automatischem Pollinations-Fallback.

## Warum dieser Skill?

- **Pollinations** ist oft instabil (HTTP 500/502 Fehler)
- **Leonardo AI** bietet Daily Credits und ist zuverlässiger
- Automatischer Fallback ohne manuelles Eingreifen

## Schnellstart

```bash
# Direkte Leonardo-Nutzung
python3 scripts/leonardo_generate.py "Ein eleganter Butler mit Zylinder" --model flux-schnell

# Mit Fallback (Pollinations zuerst, dann Leonardo)
python3 scripts/generate_with_fallback.py "Ein Roboter in der Zukunft"
```

## Modelle

### FLUX Modelle (Empfohlen)
| Modell | Stil | Verwendung |
|--------|------|------------|
| `flux-schnell` | Schnell, hochwertig | EMPFOHLEN |
| `flux-dev` | Höchste Qualität | Premium-Resultate |

### Lucid Modelle
| Modell | Stil |
|--------|------|
| `lucid-origin` | Ausgewogen |
| `lucid-realism` | Fotorealistisch |

### Leonardo XL
| Modell | Stil |
|--------|------|
| `kino-xl` | Fotorealistisch, Kino-Look |
| `vision-xl` | Allzweck |
| `anime-xl` | Anime/Manga |

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
# Leonardo AI (für Fallback)
LEONARDO_API_KEY=dein_api_key_hier

# Optional: Standard-Modell
LEONARDO_DEFAULT_MODEL=flux-schnell
```

**API Key holen:** https://leonardo.ai/ → Settings → API Keys

## Python API

```python
from scripts.leonardo_generate import LeonardoAI

client = LeonardoAI()
image = client.generate_image(
    prompt="Ein Roboter",
    model_id="1dd50843-d653-4516-a8e3-f0238ee453ff",  # FLUX.1-schnell
    width=1024,
    height=1024
)
```

## Preise

- **FLUX.1-schnell**: ~15-25 Tokens pro Bild
- **Daily Credits**: Kostenlos, resettet täglich
- Free Plan ausreichend für moderate Nutzung

---

*Teil der OpenClaw Skills Collection* 🎩
