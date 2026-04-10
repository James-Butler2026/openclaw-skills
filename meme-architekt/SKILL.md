---
name: meme-architect
description: |
  Context-Aware Meme Architect – Ein KI-Agent, der Gespräche, Texte und News 
  in passende Memes verwandelt. Nutzt die imgflip API für echte Meme-Templates 
  mit automatischer Emotionserkennung und Text-Generierung.
  
  Use when:
  1. Jemand einen lustigen Moment aus einer Konversation meme-n will
  2. Ein Erfolg/Misserfolg meme-würdig ist
  3. Ein aktuelles Ereignis als Meme visualisiert werden soll
  4. Automatische Meme-Generierung aus Chat-Kontext gewünscht ist
---

# 🎨 Context-Aware Meme Architect

Ein intelligenter Meme-Generator, der Gesprächskontext analysiert und passende Memes über die imgflip API erstellt.

## ✨ Features

- **🎭 Emotionserkennung** – Analysiert Text und wählt das passende Template
- **📝 Kontext-basierte Texte** – Generiert automatisch Ober-/Untertext
- **🖼️ Echte Meme-Templates** – Via imgflip API (keine lokalen Bilder nötig)
- **🎯 8+ Templates** – Von Success Kid bis Crying Wolverine
- **⚡ Schnell** – Direkte API-Integration mit curl

## 🚀 Schnellstart

### Installation

1. **Abhängigkeiten installieren:**
```bash
pip install Pillow
```

2. **imgflip Account erstellen:**
   - Gehe zu https://imgflip.com/signup
   - Erstelle kostenlosen Account
   - Notiere Username und Passwort

3. **.env konfigurieren:**
```bash
IMGFLIP_USERNAME=dein_username
IMGFLIP_PASSWORD=dein_passwort
```

### Nutzung

```bash
# Einzelnes Meme erstellen
python3 skills/meme-architect/scripts/meme_architect.py "Mein Code kompiliert endlich"

# Mit spezifischer Emotion
python3 skills/meme-architect/scripts/meme_architect.py "Pollinations ist down" --emotion irony

# Alle Templates anzeigen
python3 skills/meme-architect/scripts/meme_architect.py --list

# Demo-Modus (4 Beispiele)
python3 skills/meme-architect/scripts/meme_architect.py --demo
```

### In Python nutzen

```python
from skills.meme_architect.scripts.meme_architect import create_context_meme

# Erstelle Meme aus Kontext
result = create_context_meme(
    context="Endlich läuft der Cron-Job nach 3 Tagen",
    emotion="success"  # Optional: "success", "frustration", "irony", etc.
)

# Gibt den Pfad zum gespeicherten Meme zurück
print(f"Meme erstellt: {result}")
```

## 🎭 Unterstützte Emotionen & Templates

| Emotion | Template | imgflip ID | Best für |
|---------|----------|------------|----------|
| `success` | Success Kid | 61544 | Erfolge, kleine Siege |
| `frustration` | This Is Fine | 55311130 | Katastrophe ignorieren |
| `dilemma` | Two Buttons | 87743020 | Schwierige Entscheidungen |
| `superiority` | Drake Pointing | 181913649 | Ablehnung vs. Akzeptanz |
| `irony` | Distracted Boyfriend | 112126428 | Ablenkung, neue Ideen |
| `nostalgia` | Crying Wolverine | 91538330 | Nostalgie, Melancholie |
| `mocking` | Mocking Spongebob | 102156234 | Sarkasmus, Spott |
| `revelation` | Expanding Brain | 93895088 | Erleuchtung, Einsicht |

## 🏗️ Architektur

```
Input Text
    ↓
Emotionsanalyse (Keywords)
    ↓
Template-Auswahl (imgflip ID)
    ↓
Text-Generierung (Ober-/Untertext)
    ↓
API-Call an imgflip
    ↓
Bild-Download & Speicherung
    ↓
Ausgabe als PNG
```

## 📁 Dateistruktur

```
meme-architect/
├── SKILL.md                      # Diese Datei
├── README.md                     # Projekt-Übersicht
├── scripts/
│   └── meme_architect.py         # Hauptskript
└── references/
    └── imgflip-api.md            # API-Dokumentation
```

## 🔧 Konfiguration

### Umgebungsvariablen (.env)

```bash
# Erforderlich
IMGFLIP_USERNAME=dein_username
IMGFLIP_PASSWORD=dein_passwort

# Optional
MEME_OUTPUT_DIR=/tmp/meme_architect  # Standard
```

### Emotions-Trigger

Der Skill erkennt automatisch Emotionen anhand von Keywords:

```python
EMOTION_TRIGGERS = {
    "success": ["funktioniert", "geschafft", "endlich", "läuft"],
    "frustration": ["down", "fehler", "nicht", "kaputt", "bug"],
    "irony": ["toll", "super", "perfekt"],  # + negatives Kontextwort
    # ...
}
```

## 📝 Beispiele

### Beispiel 1: Erfolg
```bash
python3 meme_architect.py "Der Cron-Job läuft seit 3 Tagen ohne Fehler"
```
**Ergebnis:** Success Kid Meme mit passendem Text

### Beispiel 2: Ironie
```bash
python3 meme_architect.py "Pollinations streikt wieder, aber wenigstens haben wir noch 97 Supadata Credits"
```
**Ergebnis:** Distracted Boyfriend Meme

### Beispiel 3: Direkte Ausgabe
```bash
$ python3 meme_architect.py "API streikt? Wir bauen unseren eigenen Generator"
🎭 Erkannte Emotion: superiority
📝 Oberer Text: Manuell arbeiten
📝 Unterer Text: Automatisieren wie ein Boss
✅ Meme erstellt: /tmp/meme_architect/meme_20260410_094838.png
💾 Gespeichert unter: /tmp/meme_architect/meme_20260410_094838.png
```

**Direkter Link:** https://i.imgflip.com/aou2sd.jpg

## 🐛 Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Keine imgflip Credentials" | `.env` prüfen, Account erstellen |
| "HTTP Error 403" | curl verwendet statt urllib, funktioniert trotzdem |
| "Pillow nicht installiert" | `pip install Pillow` ausführen |
| Falsche Emotion erkannt | `--emotion` Flag verwenden |

## 🔒 Sicherheit

- **Credentials** werden nie im Code hartkodiert
- **Nur aus .env** geladen
- **Nie committen** – `.env` ist in `.gitignore`

## 📜 Lizenz

MIT License – Feel free to use and modify!

## 🎩 Credits

Erstellt für Eure Lordschaft von James, dem ergebensten Butler.

*"Ein Bild sagt mehr als 1000 Worte – aber ein Meme sagt alles auf einmal."*

---

**GitHub:** https://github.com/James-Butler2026/meme-architect
