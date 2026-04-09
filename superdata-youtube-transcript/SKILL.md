---
name: supadata-youtube-transcript
description: Supadata API Integration für YouTube-Transkripte und KI-Zusammenfassungen. Verwendet Supadata API (api.supadata.ai) um Transkripte von YouTube-Videos zu holen und automatisch Zusammenfassungen zu erstellen. Nutze diesen Skill wenn: (1) YouTube-Video-Transkripte benötigt werden, (2) Automatische Zusammenfassungen von Video-Inhalten gewünscht sind, (3) Credit-geschützte API-Integration mit Monats-Limit (Free Plan 100 Credits), (4) Integration mit bestehenden YouTube-Monitoring-Workflows. WICHTIG: Korrekte API-URL ist https://api.supadata.ai/v1 (nicht superdata.io). Credits werden NUR verbraucht wenn Transkript verfügbar ist (404 = kostenlos).
---

# Supadata YouTube Transkript Skill

Integration der Supadata API für YouTube-Transkripte mit automatischer KI-Zusammenfassung.

## Überblick

Dieser Skill ermöglicht das automatische Abrufen von YouTube-Transkripten via Supadata API und erstellt KI-gestützte Zusammenfassungen. Optimiert für den Free Plan (100 Credits/Monat).

**WICHTIG:** Korrekte API ist **Supadata** (api.supadata.ai), nicht SuperData (superdata.io).

### Core Features

- **Transkript-Abruf** via Supadata API (https://api.supadata.ai/v1)
- **KI-Zusammenfassung** mit lokalem Qwen-Modell
- **Credit-Schutz** - nur bei Erfolg verbraucht (404 = kostenlos)
- **Intelligentes Caching** - 30 Tage Cache um Duplikate zu vermeiden
- **Monatliches Tracking** - automatischer Reset bei Monatswechsel

## Schnellstart

### Einzelnes Video

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

### Mehrere Videos (Batch)

```python
from scripts.youtube_transcript_superdata import process_new_videos

videos = [
    {"id": "VIDEO_ID_1", "title": "Titel 1"},
    {"id": "VIDEO_ID_2", "title": "Titel 2"},
]

processed = process_new_videos(videos, max_videos=3)
```

### Credit-Status prüfen

```bash
python3 scripts/youtube_transcript_superdata.py --status
```

## Architektur

### Hauptmodule

| Modul | Zweck |
|-------|-------|
| `superdata_transcript.py` | Low-Level API Client für Supadata |
| `youtube_transcript_superdata.py` | High-Level Integration mit Credit-Schutz |

### Datenfluss

```
YouTube Video ID
       ↓
Cache-Prüfung (30 Tage)
       ↓
Supadata API Anfrage (GET /v1/youtube/transcript?videoId=...)
       ↓
Transkript verfügbar?
   Ja → KI-Zusammenfassung → Credit +1
   Nein → Kein Credit
       ↓
Ergebnis zurückgeben
```

## Credit-Management

### Free Plan Limits

- **100 Credits/Monat**
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

Videos werden 30 Tage in `memory/superdata_cache.json` gecacht:

```json
{
  "VIDEO_ID": {
    "checked_at": "2026-04-05T10:00:00",
    "has_transcript": true,
    "summary": "..."
  }
}
```

## Integration

### Mit YouTube Tracker

Der Skill ist direkt in `scripts/youtube_tracker.py` integriert:

```python
# Wird automatisch aufgerufen für neue Videos
from youtube_transcript_superdata import process_new_videos
processed = process_new_videos(new_videos, max_videos=3)
```

### API-Key Konfiguration

In `.env` hinzufügen:

```bash
SUPERDATA_API_KEY=sd_xxxxx
```

**Dashboard:** https://dash.supadata.ai/
**API Base URL:** https://api.supadata.ai/v1

## Fehlerbehandlung

### Häufige Fehler

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| 401 Unauthorized | Ungültiger API Key | Key in `.env` prüfen |
| 404 Not Found | Kein Transkript | Normal, kein Credit verbraucht |
| 402 Payment Required | Credits aufgebraucht | Warte auf Monatsreset |
| 429 Too Many Requests | Rate Limit | Retry mit Exponential Backoff |

## Referenzen

- **API Dokumentation**: Siehe [references/api-docs.md](references/api-docs.md)
- **Supadata Dashboard**: https://dash.supadata.ai/
- **API Endpoint**: https://api.supadata.ai/v1/youtube/transcript
