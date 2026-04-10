# imgflip API Referenz

## Übersicht

Die imgflip API ermöglicht das programmatische Erstellen von Memes mit beliebigen Templates.

**Base URL:** `https://api.imgflip.com`

## Endpoints

### GET /get_memes

Holt alle verfügbaren Meme-Templates.

**Request:**
```bash
curl https://api.imgflip.com/get_memes
```

**Response:**
```json
{
  "success": true,
  "data": {
    "memes": [
      {
        "id": "181913649",
        "name": "Drake Hotline Bling",
        "url": "https://i.imgflip.com/30b1gx.jpg",
        "width": 1200,
        "height": 1200,
        "box_count": 2
      }
    ]
  }
}
```

### POST /caption_image

Erstellt ein Meme mit angegebenem Template und Text.

**Request:**
```bash
curl -X POST https://api.imgflip.com/caption_image \
  -d "template_id=181913649" \
  -d "username=DEIN_USERNAME" \
  -d "password=DEIN_PASSWORT" \
  -d "text0=Oberer Text" \
  -d "text1=Unterer Text"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://i.imgflip.com/xyz123.jpg",
    "page_url": "https://imgflip.com/i/xyz123"
  }
}
```

## Parameter

### caption_image

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `template_id` | string | Ja | ID des Meme-Templates |
| `username` | string | Ja | imgflip Username |
| `password` | string | Ja | imgflip Passwort |
| `text0` | string | Nein | Oberer Text |
| `text1` | string | Nein | Unterer Text |

### Boxen-Parameter (für komplexe Memes)

Für Memes mit mehr als 2 Textfeldern können box-Parameter verwendet werden:

```bash
-d "boxes[0][text]=Erster Text" \
-d "boxes[0][x]=10" \
-d "boxes[0][y]=10" \
-d "boxes[0][width]=100" \
-d "boxes[0][height]=50" \
-d "boxes[0][color]=#ffffff" \
-d "boxes[0][outline_color]=#000000"
```

## Fehler-Codes

| Code | Bedeutung |
|------|-----------|
| 200 | Erfolg |
| 401 | Ungültige Credentials |
| 404 | Template nicht gefunden |
| 500 | Server-Fehler |

## Rate Limits

- Keine offiziellen Rate Limits dokumentiert
- Fair Use: Nicht mehrere Requests pro Sekunde

## Beliebte Template IDs

| ID | Name |
|----|------|
| 181913649 | Drake Hotline Bling |
| 87743020 | Two Buttons |
| 112126428 | Distracted Boyfriend |
| 61544 | Success Kid |
| 93895088 | Expanding Brain |
| 55311130 | This Is Fine |
| 91538330 | Crying Wolverine |
| 102156234 | Mocking Spongebob |

## Referenzen

- **Dokumentation:** https://imgflip.com/api
- **Meme Templates:** https://imgflip.com/memetemplates

## Hinweise

- Alle generierten Memes sind öffentlich auf imgflip sichtbar
- Für private Memes: Account-Einstellungen prüfen
- Text sollte kurz sein (max ~50 Zeichen pro Feld)
