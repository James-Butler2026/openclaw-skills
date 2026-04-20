# Leonardo Image Generation Skill for OpenClaw

Professionelle Bildgenerierung mit Leonardo AI API und automatischem Pollinations-Fallback.

## ✨ Features

- **🎨 Leonardo AI Integration** - Zugriff auf 14+ hochwertige KI-Modelle
- **⚡ FLUX.1-schnell** - Schnellstes Open-Source Bildgenerierungsmodell
- **🔄 Automatischer Fallback** - Wechselt zu Pollinations bei Leonardo-Ausfall
- **📊 Modell-Vielfalt** - Von fotorealistisch bis fantasievoll
- **🔒 Sicher** - API-Keys werden niemals im Code gespeichert

## 🖼️ Unterstützte Modelle

### FLUX Modelle (Empfohlen)
| Modell | ID | Verwendung |
|--------|-----|------------|
| **FLUX.1-schnell** | `1dd50843-d653-4516-a8e3-f0238ee453ff` | Schnell, hochwertig |
| **FLUX.1-dev** | `b2614463-296c-462a-9586-aafdb8f00e36` | Höchste Qualität |

### Lucid Modelle (Sehr gute Qualität)
| Modell | ID | Stil |
|--------|-----|------|
| **Lucid Origin** | `7b592283-e8a7-4c5a-9ba6-d18c31f258b9` | Ausgewogen |
| **Lucid Realism** | `05ce0082-2d80-4a2d-8653-4d1c85e2418e` | Fotorealistisch |

### Leonardo XL Modelle
| Modell | ID | Stil |
|--------|-----|------|
| **Leonardo Anime XL** | `e71a1c2f-4f80-4800-934f-2c68979d8cc8` | Anime/Manga |
| **Leonardo Lightning XL** | `b24e16ff-06e3-43eb-8d33-4416c2d75876` | Sehr schnell |
| **Leonardo Kino XL** | `aa77f04e-3eec-4034-9c07-d0f619684628` | Kino-Look |
| **Leonardo Vision XL** | `5c232a9e-9061-4777-980a-ddc8e65647c6` | Allzweck |

### Spezialisierte Modelle
| Modell | ID | Verwendung |
|--------|-----|------------|
| **RPG v5** | `f1929ea3-b169-4c18-a16c-5d58b4292c69` | Charaktere, Fantasy |
| **DreamShaper v7** | `ac614f96-1082-45bf-be9d-757f2d31c17` | Kreative Kunst |
| **AlbedoBase XL** | `2067ae52-33fd-4a82-bb92-c2c55e7d2786` | Gemälde, Illustrationen |

## 🚀 Schnellstart

### 1. Leonardo AI Account erstellen
1. Gehe zu: https://leonardo.ai/
2. Erstelle kostenlosen Account
3. Generiere API Key unter: Settings → API Keys

### 2. Konfiguration
Füge zu deiner `.env` Datei hinzu:
```bash
LEONARDO_API_KEY=dein_api_key_hier
```

### 3. Nutzung

#### Direkte Leonardo-Nutzung
```bash
python3 scripts/leonardo_generate.py "Ein elegantes Maskottchen mit Zylinder" --model flux-schnell
```

#### Mit Fallback (empfohlen)
```bash
python3 scripts/generate_with_fallback.py "Ein majestätischer Hummer" --model flux-schnell
```

#### In Python
```python
from scripts.leonardo_generate import LeonardoAI

client = LeonardoAI()
result = client.generate_image(
    prompt="Ein Roboter liest ein Buch",
    model_id="1dd50843-d653-4516-a8e3-f0238ee453ff",  # FLUX.1-schnell
    width=1024,
    height=1024
)
```

## 📋 CLI-Parameter

### leonardo_generate.py
```bash
python3 leonardo_generate.py [OPTIONS] PROMPT

Options:
  --model, -m {flux-schnell,flux-dev,lucid-origin,lucid-realism,anime-xl,lightning-xl,kino-xl,vision-xl,rpg-v5,dreamshaper-v7,albedobase-xl}
                        Zu verwendendes Modell (default: vision-xl)
  --width, -W {512,768,1024}   Bildbreite (default: 1024)
  --height, -H {512,768,1024}  Bildhöhe (default: 1024)
  --num, -n N            Anzahl Bilder (1-8, default: 1)
  --output, -o PATH      Ausgabepfad
  --info                 Account-Info anzeigen
  --list-models          Alle Modelle anzeigen
```

### generate_with_fallback.py
```bash
python3 generate_with_fallback.py [OPTIONS] PROMPT

Options:
  --model, -m {flux-schnell,flux-dev,lucid-origin,lucid-realism,...}
  --width, -W {512,768,1024}
  --height, -H {512,768,1024}
  --output, -o PATH
```

## 💰 Kosten

- **Leonardo AI:** Daily Credits (kostenlos), danach Bezahlung
- **Pollinations:** Kostenlos (Fallback)
- **Preis pro Bild:** ~15-50 Tokens (aus Daily Credits)

## 🔧 Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Invalid model ID" | ID aus README verwenden |
| "Rate limit exceeded" | Daily Credits aufgebraucht |
| "API Key invalid" | Key in .env prüfen |
| Bildqualität schlecht | Anderes Modell probieren |

## 📝 Beispiele

### Kinderbuch-Illustration
```bash
python3 leonardo_generate.py "A cute cartoon turtle reading a colorful book" --model lucid-origin --width 768 --height 768
```

### Fotorealistisches Portrait
```bash
python3 leonardo_generate.py "A distinguished Victorian butler in formal attire" --model lucid-realism --width 1024 --height 1024
```

### Anime-Stil
```bash
python3 leonardo_generate.py "A young wizard casting spells" --model anime-xl --width 768 --height 1024
```

## 🔗 Weitere Ressourcen

- **Leonardo AI Docs:** https://docs.leonardo.ai/
- **FLUX Modelle:** https://blackforestlabs.ai/
- **API-Referenz:** `GET /platformModels` für alle verfügbaren Modelle

## 🤝 Integration in OpenClaw

Dieser Skill ist Teil des OpenClaw Workspace-Systems:
- Automatisches Laden aus `skills/leonardo-image-gen/`
- Integration mit Workspace-`.env`
- Konsistente Logging und Fehlerbehandlung

## 📜 Lizenz

MIT License - Siehe [LICENSE](../../LICENSE)

---

*Erstellt für OpenClaw von OpenClaw User, vom Assistenten* 🎩
