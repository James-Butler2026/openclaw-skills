# Leonardo AI Image Generation Skill

Bildgenerierung via Leonardo AI API mit Pollinations-Fallback.

## Übersicht

Dieser Skill bietet zuverlässige Bildgenerierung mit folgender Priorität:
1. **Pollinations.ai** (kostenlos, Standard)
2. **Leonardo AI** (Fallback bei Pollinations-Ausfall)

## Warum dieser Skill?

- **Pollinations** ist oft instabil (HTTP 500/502 Fehler)
- **Leonardo AI** bietet Daily Credits (kostenlos) und ist zuverlässiger
- Automatischer Fallback ohne manuelles Eingreifen

## Modelle

### Verfügbare Modelle bei Leonardo AI

#### FLUX Modelle (Empfohlen)
| Modell | ID | Stil | Verwendung |
|--------|-----|------|------------|
| **FLUX.1-schnell** | `1dd50843-d653-4516-a8e3-f0238ee453ff` | Schnell, hochwertig | EMPFOHLEN |
| **FLUX.1-dev** | `b2614463-296c-462a-9586-aafdb8f00e36` | Höchste Qualität | Für Premium-Resultate |

#### Lucid Modelle (Sehr gute Qualität)
| Modell | ID | Stil | Verwendung |
|--------|-----|------|------------|
| **Lucid Origin** | `7b592283-e8a7-4c5a-9ba6-d18c31f258b9` | Ausgewogen | Allzweck |
| **Lucid Realism** | `05ce0082-2d80-4a2d-8653-4d1c85e2418e` | Fotorealistisch | Realistische Bilder |

#### Leonardo XL Modelle
| Modell | ID | Stil | Verwendung |
|--------|-----|------|------------|
| **Leonardo Anime XL** | `e71a1c2f-4f80-4800-934f-2c68979d8cc8` | Anime/Manga | Japanischer Stil |
| **Leonardo Lightning XL** | `b24e16ff-06e3-43eb-8d33-4416c2d75876` | Sehr schnell | Speed-Priority |
| **Leonardo Kino XL** | `aa77f04e-3eec-4034-9c07-d0f619684628` | Fotorealistisch | Kino-Look |
| **Leonardo Vision XL** | `5c232a9e-9061-4777-980a-ddc8e65647c6` | Allzweck | Standard |

#### Spezialisierte Modelle
| Modell | ID | Stil | Verwendung |
|--------|-----|------|------------|
| **RPG v5** | `f1929ea3-b169-4c18-a16c-5d58b4292c69` | Rollenspiel | Charaktere, Fantasy |
| **DreamShaper v7** | `ac614f96-1082-45bf-be9d-757f2d31c17` | Fantasievoll | Kreative Kunst |
| **AlbedoBase XL** | `2067ae52-33fd-4a82-bb92-c2c55e7d2786` | Vielseitig | Gemälde, Illustrationen |

## API-Dokumentation

Offizielle Leonardo AI Docs: https://docs.leonardo.ai/docs/getting-started

### Schnellstart

1. Account erstellen: https://leonardo.ai/
2. API Key generieren: Settings → API Keys
3. `.env` aktualisieren: `LEONARDO_API_KEY=dein_key`

## Verwendung

```python
from skills.leonardo_image_gen.scripts.leonardo_generate import generate_image_with_fallback

# Automatischer Fallback
result = generate_image_with_fallback(
    prompt="Ein eleganter Butler mit Zylinder",
    output_path="/tmp/bild.png",
    width=1024,
    height=1024
)

# Oder direkt Leonardo
from skills.leonardo_image_gen.scripts.leonardo_generate import LeonardoAI

client = LeonardoAI()
image = client.generate_image(
    prompt="Ein Roboter",
    model_id="1dd50843-d653-4516-a8e3-f0238ee453ff",  # FLUX.1-schnell
    width=1024,
    height=1024
)
```

## CLI-Nutzung

```bash
# Direkte Leonardo-Nutzung
python3 skills/leonardo-image-gen/scripts/leonardo_generate.py "Prompt" --model flux-schnell

# Mit Fallback (Pollinations zuerst, dann Leonardo)
python3 skills/leonardo-image-gen/scripts/generate_with_fallback.py "Prompt"
```

## Konfiguration

### .env Variablen

```bash
# Leonardo AI (für Fallback)
LEONARDO_API_KEY=dein_api_key_hier

# Optional: Standard-Modell
LEONARDO_DEFAULT_MODEL=flux-schnell
```

### Preise

- **FLUX.1-schnell**: ~15-25 Tokens pro Bild (aus Daily Credits)
- **Andere Modelle**: Je nach Modell 10-50 Tokens
- **Daily Credits**: Kostenlos, resettet täglich

## Troubleshooting

### "Invalid model ID"
- Prüfe die Modell-ID in der Dokumentation
- Manche IDs ändern sich bei Updates

### "Rate limit exceeded"
- Daily Credits aufgebraucht
- Warte bis zum nächsten Tag oder upgrade Account

### Bildqualität schlecht
- Prompt optimieren (mehr Details, bessere Beschreibung)
- Anderes Modell probieren (kino-xl für Fotos, dreamshaper für Fantasy)
- Auflösung erhöhen (1024x1024 statt 512x512)

## Vergleich: Pollinations vs Leonardo

| Feature | Pollinations | Leonardo AI |
|---------|--------------|-------------|
| Kosten | Kostenlos | Daily Credits (kostenlos) |
| Zuverlässigkeit | ⚠️ Instabil | ✅ Stabil |
| Geschwindigkeit | ⚡ Schnell | ⚡ Schnell |
| Qualität | ⭐⭐⭐ Gut | ⭐⭐⭐⭐⭐ Sehr gut |
| Rate Limits | ❌ Unbekannt | ✅ Transparent |

## Fallback-Logik

```
1. Versuche Pollinations.ai
   ↓ Falls Fehler (HTTP 5xx, Timeout)
2. Wechsle zu Leonardo AI
   ↓ Falls auch Fehler
3. Fehlermeldung mit Details
```

## Git

- **Private Git**: ✅ Committen
- **Online Git (GitHub)**: ❌ Nicht pushen (API Keys!)

## Changelog

### 2026-04-11
- Initialer Skill mit FLUX.1-schnell Unterstützung
- Fallback-Logik Pollinations → Leonardo
- Dokumentation aller verfügbaren Modelle

---
*Skill erstellt von James, dem ergebensten Butler* 🎩
