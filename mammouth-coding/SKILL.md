# Mammouth.ai Coding Skill

Verwendet mammouth.ai API mit Claude Opus 4-6 NUR für Code-Generierung.

## Verwendung

```bash
# Script generieren (Standard: claude-opus-4-6)
python3 scripts/mammouth_coder.py "Erstelle ein Script für..."

# Mit anderem Modell
python3 scripts/mammouth_coder.py "Beschreibung..." --model claude-sonnet-4-6

# Mit Retry-Versuchen
python3 scripts/mammouth_coder.py "Beschreibung..." --retries 3

# Oder direkt in Python
python3 -c "
from scripts.mammouth_coder import generate_code
code = generate_code('Beschreibung...', language='python')
print(code)
"
```

## Regel

- ✅ **NUR für Code-Generierung**
- ❌ **NIE für Chat, Exec, Thinking, Web-Suche**
- Default für alles andere: qwen (wie gewohnt)

## API Key

In `.env`:
```
MAMMOUTH_API_KEY=[REDACTED]
```

## Modell

- `claude-opus-4-6` für bestes Coding & Nuancenverständnis (ab 25.03.2026)
- `claude-sonnet-4-6` als Alternative (Goldstandard für Geschwindigkeit/Power)

## Verbesserungen (25.03.2026)

### 1. Zentrales Logging
Alle Scripts nutzen jetzt `scripts/logger_config.py`:
- Logs werden in `logs/james.log` gespeichert
- RotatingFileHandler (5 MB, 5 Backups)
- Console-Output für direkte Nutzung

### 2. Bessere Fehlerbehandlung
Spezifische Exceptions statt generischer:
- `MammouthAPIKeyError` - Kein API Key
- `MammouthAPIError` - API-Fehler (HTTP 4xx/5xx)
- `MammouthResponseError` - Ungültige Antwort

### 3. Retry-Mechanismus
Bei vorübergehenden Fehlern automatisch retry:
- Standard: 2 Retries
- Exponentielles Backoff (2^n Sekunden)
- Kein Retry bei Auth-Fehlern (401/403)

### 4. Exit-Codes
Für Automatisierung/Scripting:
- `0` - Erfolg
- `1` - Kein API Key
- `2` - API-Fehler
- `3` - Ungültige Antwort

## Beispiel: Verbessertes Fehlerhandling

```python
from scripts.mammouth_coder import generate_code, MammouthAPIError

try:
    code = generate_code("Erstelle API", retries=3)
    if code:
        print(code)
except MammouthAPIKeyError:
    print("API Key fehlt!")
except MammouthAPIError as e:
    print(f"API Fehler: {e}")
```
