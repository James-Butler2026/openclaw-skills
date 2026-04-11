# Supadata YouTube Transcript Skill

YouTube-Transkripte mit Supadata API und KI-Zusammenfassungen.

## Features

- 🎥 **Transkript-Abruf** via Supadata API
- 🤖 **KI-Zusammenfassung** mit lokalem Modell
- 💰 **Credit-Schutz** - Nur bei Erfolg verbraucht (404 = kostenlos)
- 💾 **30-Tage-Cache** - Vermeidet Duplikate
- 📊 **Monatliches Tracking** - Automatischer Reset

## Schnellstart

```python
from scripts.youtube_transcript_superdata import get_transcript_summary

result = get_transcript_summary(
    video_id="dQw4w9WgXcQ",
    video_title="Never Gonna Give You Up",
    language="de"
)

if result:
    print(f"Zusammenfassung: {result['summary']}")
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
SUPERDATA_API_KEY=sd_dein_key_hier
```

**API Key holen:** https://dash.supadata.ai/

**Free Plan:** 100 Credits/Monat

## Credit-Management

### Limits

- **100 Credits/Monat** (Free Plan)
- **1 Credit = 1 Video mit Transkript**
- **0 Credits = Video ohne Transkript** (404 Response)

### Tracking

Credits werden in `memory/superdata_credits.json` gespeichert:

```json
{
  "month": "2026-04",
  "used": 15,
  "remaining": 85,
  "videos_processed": [...]
}
```

Automatischer Reset bei Monatswechsel.

### Cache

Videos werden 30 Tage in `memory/superdata_cache.json` gecacht.

## Fehlerbehandlung

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| 401 Unauthorized | Ungültiger API Key | Key in `.env` prüfen |
| 404 Not Found | Kein Transkript | Normal, kein Credit verbraucht |
| 402 Payment Required | Credits aufgebraucht | Warte auf Monatsreset |
| 429 Too Many Requests | Rate Limit | Retry mit Backoff |

## Wichtiger Hinweis

Die korrekte API ist **Supadata** (api.supadata.ai), nicht SuperData (superdata.io).

---

*Teil der OpenClaw Skills Collection* 🎩
