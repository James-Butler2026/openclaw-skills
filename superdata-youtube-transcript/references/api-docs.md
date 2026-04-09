# SuperData API Dokumentation

## Überblick

SuperData API bietet Zugriff auf YouTube-Transkripte für automatisierte Verarbeitung.

**Website:** https://superdata.io/
**Base URL:** `https://api.superdata.io/v1`
**Authentifizierung:** Bearer Token im Authorization Header

## Endpoints

### POST /youtube/transcript

Holt das Transkript für ein YouTube-Video.

#### Request

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "de"
}
```

#### Response (Erfolg)

```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "transcript": "Hier steht das vollständige Transkript...",
  "is_generated": true,
  "duration": 212,
  "language": "de"
}
```

**Felder:**
- `transcript` (string): Vollständiger Transkript-Text
- `is_generated` (bool): `true` = Auto-Transkript von YouTube, `false` = Manuelle Untertitel
- `duration` (int): Videolänge in Sekunden
- `language` (string): ISO 639-1 Sprachcode

#### Response (Kein Transkript)

HTTP 404

```json
{
  "error": "No transcript available"
}
```

**WICHTIG:** Bei 404 wird KEIN Credit verbraucht!

#### Response (Credits aufgebraucht)

HTTP 402

```json
{
  "error": "Credits exhausted"
}
```

## Credit-System

### Free Plan

| Feature | Limit |
|---------|-------|
| Credits/Monat | 100 |
| Kosten pro Transkript | 1 Credit (nur bei Erfolg) |
| Kosten bei 404 | 0 Credits |

### Credit-Verbrauch

Credits werden NUR verbraucht wenn:
1. HTTP 200 zurückkommt
2. `transcript` Feld enthält Text

Credits werden NICHT verbraucht bei:
- HTTP 404 (kein Transkript verfügbar)
- HTTP 401 (ungültiger Key)
- HTTP 429 (Rate Limit)

## Authentifizierung

```bash
curl -X POST https://api.superdata.io/v1/youtube/transcript \
  -H "Authorization: Bearer sd_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "VIDEO_ID", "language": "de"}'
```

## Fehlercodes

| Code | Bedeutung | Credit-Verbrauch |
|------|-----------|------------------|
| 200 | Erfolg | Ja (1) |
| 401 | Ungültiger API Key | Nein |
| 404 | Kein Transkript | Nein |
| 402 | Credits aufgebraucht | Nein |
| 429 | Rate Limit | Nein |
| 500 | Serverfehler | Nein |

## Best Practices

### 1. Caching implementieren

Videos sollten 30 Tage gecacht werden um Duplikate zu vermeiden.

### 2. Credit-Tracking

Monatliches Tracking mit automatischem Reset:

```python
def get_credit_status():
    state = load_state()
    if state["month"] != current_month:
        return reset_credits()  # Neuer Monat
```

### 3. Sprachpräferenz

Standardmäßig `"de"` für Deutsch verwenden. Die API versucht Fallback auf verfügbare Sprachen.

### 4. Fehlerbehandlung

404 ist ein NORMALES Ergebnis, kein Fehler. Viele Videos haben keine Transkripte.

## Python-Beispiel

```python
import urllib.request
import json

def get_transcript(video_id, api_key, language="de"):
    url = "https://api.superdata.io/v1/youtube/transcript"
    
    payload = json.dumps({
        "video_id": video_id,
        "language": language
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"has_transcript": False}
        raise
```

## Unterstützte Plattformen

- YouTube (Standard)
- YouTube Music (experimentell)
- YouTube Shorts (teilweise)

## Limits

| Limit | Wert |
|-------|------|
| Rate Limit | 60 Requests/Minute |
| Timeout | 30 Sekunden |
| Max Transkript-Länge | ~50.000 Zeichen |
