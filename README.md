# OpenClaw Skills Collection

Eine Sammlung nützlicher Skills für OpenClaw – vollständig lokal nutzbar, dokumentiert und API-sicher konfiguriert.

## 📋 Übersicht

Diese Sammlung enthält **14 praxisnahe Skills** für OpenClaw – von Audio-Transkription über Bildgenerierung bis hin zu Krypto-Portfolio-Tracking. Alle Skills sind offline-fähig, datenschutzfreundlich und ohne Cloud-Abhängigkeit.

| Skill | Beschreibung | Kategorie |
|-------|--------------|-----------|
| [ap1-training-tracker](#ap1-training-tracker) | IHK Fachinformatiker AP1 Training mit 280 Fragen | Lernen |
| [audio-transcription](#audio-transcription) | Audio zu Text mit Whisper (faster-whisper) | Audio |
| [calendar](#calendar) | Lokaler Kalender mit natürlicher Spracheingabe | Produktivität |
| [crypto-tracker](#crypto-tracker) | Krypto-Portfolio-Tracking für BTC, ETH, SOL, XRP | Finanzen |
| [elevenlabs-tts](#elevenlabs-tts) | Text-to-Speech via ElevenLabs API | Audio |
| [email-sender](#email-sender) | E-Mails via SMTP senden | Kommunikation |
| [expense-tracker](#expense-tracker) | Budget-Tracking mit Einkommen, Fixkosten, Ersparnissen | Finanzen |
| [github-manager](#github-manager) | Skills zu GitHub veröffentlichen | Entwicklung |
| [image-generation](#image-generation) | Kostenlose Bildgenerierung via Pollinations.ai | Bild |
| [leonardo-image-gen](#leonardo-image-gen) | Bildgenerierung mit Leonardo AI | Bild |
| [mammouth-coding](#mammouth-coding) | Code-Generierung mit Mammouth.ai | Entwicklung |
| [meme-architect](#meme-architect) | Meme-Generierung mit imgflip API | Spaß |
| [mega-filehoster](#mega-filehoster) | MEGA.nz Cloud Storage Verwaltung | Storage |
| [package-tracking](#package-tracking) | Einheitliches Paket-Tracking für Hermes + DHL | Tracking |
| [piper-tts](#piper-tts) | Deutsche Text-to-Speech (lokal) | Audio |
| [superdata-youtube-transcript](#superdata-youtube-transcript) | YouTube-Transkripte mit Supadata API | Video |
| [tavily-search](#tavily-search) | Websuche via Tavily API | Recherche |
| [wordpress-manager](#wordpress-manager) | WordPress Beiträge via REST API verwalten | CMS |

---

## 🚀 Schnellstart

### Einen Skill installieren

```bash
# Repository klonen
git clone https://github.com/James-Butler2026/openclaw-skills.git

# In den Skill-Ordner wechseln
cd openclaw-skills/audio-transcription/

# SKILL.md lesen für Setup-Anleitung
cat SKILL.md
```

### Voraussetzungen

Die meisten Skills benötigen:
- Python 3.8+
- OpenClaw Workspace (empfohlen)
- `.env` Datei im Workspace-Root mit entsprechenden API-Keys

---

## 📦 Skills im Detail

### ap1-training-tracker
**IHK Fachinformatiker AP1 Training**

- 280 Fragen aus dem IHK-Prüfungsstoff
- 50 subnetting-spezifische Fragen
- Interaktives Training mit Feedback
- Automatische Statistiken und Fortschrittsanzeige
- SQLite-basierte Datenbank

```bash
python3 scripts/ap1_training.py
python3 scripts/ap1_tracker.py --daily
```

→ [Details ansehen](ap1-training-tracker/README.md)

---

### audio-transcription
**Audio zu Text Transkription mit faster-whisper**

- Unterstützt: MP3, OGG, WAV, etc.
- Mehrere Modelle: tiny bis large-v3
- Auto-Detect Sprache oder explizit angeben
- Deutsche Sprache nativ unterstützt

```bash
python3 scripts/transcribe.py audio.mp3 --language de
```

→ [Details ansehen](audio-transcription/README.md)

---

### crypto-tracker
**Krypto-Portfolio-Tracking für BTC/XRP**

- Echtzeit-Kurse via CoinGecko API
- Gewinn/Verlust-Berechnung
- Stop-Loss bei -20%, Take-Profit bei +25%
- Performance-Vergleich
- SQLite-basiert

```bash
python3 scripts/bison_tracker.py --init
python3 scripts/bison_tracker.py --status
```

→ [Details ansehen](crypto-tracker/README.md)

---

### calendar
**Lokaler Kalender mit natürlicher Spracheingabe**

- Natürliche Sprache: *"Termin morgen 14 Uhr"*
- Geburtstage mit jährlichen Erinnerungen
- Automatische Cron-Erinnerungen
- Wiederholungen: täglich, wöchentlich, monatlich, jährlich
- SQLite-basiert, keine Cloud

```bash
python3 scripts/calendar_cli.py "Termin morgen 14 Uhr mit Dr. Kaufmann"
python3 scripts/calendar_cli.py --today
```

→ [Details ansehen](calendar/README.md)

---

### package-tracking
**Einheitliches Paket-Tracking für Hermes + DHL**

- Zentraler Manager für alle Pakete
- SQLite-Datenbank mit Tracking-Verlauf
- Automatische Checks um 10:00 und 16:00 Uhr
- Telegram-Updates bei Status-Änderungen
- Retry-Logik für API-Fehler

```bash
# Paket hinzufügen
python3 scripts/package_manager.py add -c [CODE] -r hermes -d "Beschreibung"

# Alle Pakete tracken
python3 scripts/package_manager.py track --json

# Übersicht anzeigen
python3 scripts/package_manager.py list
```

**Architektur:**
- `package_manager.py` - Hauptscript (Koordination, DB)
- `hermes_tracker.py` - Hermes via Browser + OCR
- `dhl_tracker.py` - DHL via REST API

→ [Details ansehen](package-tracking/SKILL.md)

---

### email-sender
**E-Mails via SMTP senden**

- Unterstützt: Web.de, Gmail, GMX, eigene SMTP-Server
- App-Passwörter für Gmail
- Einfache Python API
- Keine externen Abhängigkeiten

```bash
python3 scripts/send_email.py --to empfaenger@example.com \
    --subject "Hallo" --body "Testnachricht"
```

→ [Details ansehen](email-sender/README.md)

---

### expense-tracker
**Budget-Tracking mit Einkommen, Fixkosten & Ersparnissen (v3.0)**

- 🎤 Spracheingabe: *"Habe 12,50€ bei Rewe ausgegeben"*
- 💰 Einkommen & Fixkosten-Verwaltung
- 📊 Budget-Übersicht: Einkommen – Fixkosten – Variabel = Ersparnisse
- 📅 ISO-KW (Mo-So) + Monatswochen (1.-7., 8.-14. etc.)
- 📋 Detail-Aufschlüsselung bei jedem Report
- 🗓️ Jahresübersicht & Gesamt-Übersicht
- ⏱️ Temporäre Fixkosten mit Enddatum
- 🔢 Cent-genaue Beträge, keine Rundung
- 💾 Monats-Zusammenfassungen werden gespeichert
- SQLite-basiert, keine Cloud

```bash
python3 scripts/expense_tracker.py "12,50€ bei Rewe"
python3 scripts/expense_tracker.py --weekly          # Diese Woche (Mo-So)
python3 scripts/expense_tracker.py --last-week        # Letzte Woche
python3 scripts/expense_tracker.py --month-to-date    # 1. bis heute
python3 scripts/expense_tracker.py --monthly          # Budget-Bericht
python3 scripts/expense_tracker.py --year             # Jahresübersicht
python3 scripts/expense_tracker.py --total             # Gesamt-Übersicht
```

→ [Details ansehen](expense-tracker/README.md)

---

### github-manager
**Skills zu GitHub veröffentlichen**

- Repository erstellen
- Einzelne oder alle Skills synchronisieren
- Automatische README-Generierung
- GitHub Actions Integration

```bash
python3 scripts/github_publish.py --skill image-generation --repo openclaw-skills
```

→ [Details ansehen](github-manager/README.md)

---

### image-generation
**Kostenlose Bildgenerierung via Pollinations.ai**

- Kein API-Key nötig
- Keine Rate-Limits bekannt
- Custom Dimensionen und Seeds
- Watermark-freier Output

```bash
python3 scripts/generate_image.py "A beautiful sunset" --width 1024 --height 768
```

→ [Details ansehen](image-generation/README.md)

---

### leonardo-image-gen
**Bildgenerierung mit Leonardo AI + Pollinations-Fallback**

- Leonardo AI API (Daily Credits)
- Automatischer Fallback zu Pollinations
- FLUX.1, Lucid, Leonardo XL Modelle
- Höhere Qualität als Pollinations allein

```bash
python3 scripts/leonardo_generate.py "Ein elegantes Maskestück" --model flux-schnell
```

→ [Details ansehen](leonardo-image-gen/README.md)

---

### mammouth-coding
**Code-Generierung mit Claude Opus 4-6**

- **NUR für Code-Generierung**
- Mammouth.ai API
- Retry-Mechanismus mit Exponential Backoff
- Bessere Fehlerbehandlung

```bash
python3 scripts/mammouth_coder.py "Erstelle eine Python-Klasse für..."
```

→ [Details ansehen](mammouth-coding/README.md)

---

### meme-architect
**Meme-Generierung mit imgflip API**

- Automatische Meme-Erstellung aus Kontext
- Unterstützung für imgflip Meme-Templates
- Emotionserkennung für passende Memes
- Text-Generierung basierend auf Vorlagen
- Einfache CLI-Nutzung

```bash
python3 scripts/meme_architect.py "lustiger Moment"
```

→ [Details ansehen](meme-architect/README.md)

---

### mega-filehoster
**MEGA.nz Cloud Storage Verwaltung**

- Dateien hochladen/herunterladen
- Verzeichnisse auflisten
- Share-Links generieren
- Speicherplatz prüfen

```bash
python3 scripts/mega_manager.py upload /pfad/zur/datei.txt
```

→ [Details ansehen](mega-filehoster/README.md)

---

### piper-tts
**Deutsche Text-to-Speech (lokal)**

- Thorsten-Stimme (deutsch, männlich)
- Kein API-Key nötig
- Lokale Ausführung
- Telegram Voice-Messages

```bash
python3 scripts/piper_tts.py "Hallo Welt" --send
```

→ [Details ansehen](piper-tts/README.md)

---

### elevenlabs-tts
**Text-to-Speech via ElevenLabs API**

- Unterstützung für 70+ Sprachen
- Mehrere Modelle: multilingual_v2, turbo, flash
- Custom Voice Cloning
- Streaming-Unterstützung
- Exzellente deutsche Aussprache

```bash
python3 scripts/elevenlabs_tts.py speak "Hallo Welt" --voice VOICE_ID
```

→ [Details ansehen](elevenlabs-tts/README.md)

---

### superdata-youtube-transcript
**YouTube-Transkripte mit Supadata API**

- Supadata API (100 Credits/Monat Free)
- KI-Zusammenfassungen
- 30-Tage-Cache
- Nur Credits bei Erfolg

```python
from scripts.youtube_transcript_superdata import get_transcript_summary
result = get_transcript_summary(video_id="...")
```

→ [Details ansehen](superdata-youtube-transcript/README.md)

---

### tavily-search
**Websuche via Tavily API**

- AI-generierte Zusammenfassungen
- Relevance Scores
- Strukturierte Ergebnisse
- Quellenangaben

```bash
python3 scripts/tavily_search.py "KI Entwicklungen 2026" --depth advanced
```

→ [Details ansehen](tavily-search/README.md)

---

### wordpress-manager
**WordPress Beiträge verwalten**

- REST API Integration
- Cloudflare-kompatibel
- CRUD-Operationen
- Kategorien & Tags

```bash
python3 scripts/wordpress_manager.py --create "Titel" "HTML-Inhalt"
```

→ [Details ansehen](wordpress-manager/README.md)

---

## ⚙️ Konfiguration

### .env Variablen

Die meisten Skills benötigen eine `.env` Datei im OpenClaw-Workspace:

```bash
# OpenClaw Workspace Root
~/.openclaw/workspace/.env
```

Siehe die einzelnen Skill-READMEs für die benötigten Variablen.

### Ordnerstruktur

```
~/.openclaw/workspace/
├── .env                          # API-Keys und Konfiguration
├── skills/
│   ├── audio-transcription/
│   ├── crypto-tracker/
│   ├── package-tracking/
│   ├── ...
│   └── wordpress-manager/
├── scripts/                      # Skill-Scripts
└── data/                         # Datenbanken, Caches
```

---

## 🤝 Mitwirken

Skills werden fortlaufend erweitert. Vorschläge und Pull Requests sind willkommen!

---

## 📜 Lizenz

Alle Skills sind unter MIT-Lizenz veröffentlicht.