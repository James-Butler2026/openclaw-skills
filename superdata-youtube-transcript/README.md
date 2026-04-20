# SuperData YouTube Transcript Skill

YouTube-Transkripte mit Supadata API – schnell und zuverlässig.

## Features

- 🎬 Supadata API (100 Credits/Monat Free)
- 🤖 KI-Zusammenfassungen
- 💾 30-Tage-Cache
- ✅ Nur Credits bei Erfolg

## Installation

```bash
cd ~/.openclaw/workspace/skills/superdata-youtube-transcript/
```

## Verwendung

```bash
# Transkript holen
python3 scripts/youtube_transcript_superdata.py VIDEO_ID

# Mit Zusammenfassung
python3 scripts/youtube_transcript_superdata.py VIDEO_ID --summary

# In Python nutzen
from scripts.youtube_transcript_superdata import get_transcript_summary
result = get_transcript_summary(video_id="dQw4w9WgXcQ")
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
SUPADATA_API_KEY=dein_api_key_hier
```

**Key holen:** https://supadata.ai

## Sicherheit

- API-Key niemals committen
- Nur Video-IDs werden verarbeitet
- Keine persönlichen Daten

---
*YouTube-Transkription für OpenClaw* 🎬
