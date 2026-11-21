<div align="center">

# 🧩 OpenClaw Skills

**20 praxiserprobte Skills für OpenClaw-Agenten: Audio, Bild, Finanzen, Tracking, Produktivität und Entwicklung.**

Jeder Skill bringt eine `SKILL.md` (Anleitung für den Agenten), ein `README.md` und lauffähige Python-Skripte mit.

[![Skills](https://img.shields.io/badge/Skills-20-8A2BE2?style=for-the-badge)](#-alle-skills-im-überblick)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-lokal-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](#)
[![Sprache](https://img.shields.io/badge/Sprache-Deutsch-black?style=for-the-badge)](#)

[![Last Commit](https://img.shields.io/github/last-commit/James-Butler2026/openclaw-skills?style=flat-square)](https://github.com/James-Butler2026/openclaw-skills/commits)
[![Repo Size](https://img.shields.io/github/repo-size/James-Butler2026/openclaw-skills?style=flat-square)](https://github.com/James-Butler2026/openclaw-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Schnellstart](#-schnellstart) · [Skills](#-alle-skills-im-überblick) · [Details](#-skills-im-detail) · [Konfiguration](#%EF%B8%8F-konfiguration) · [Mitwirken](#-mitwirken)

</div>

---

## ✨ Warum diese Sammlung?

- 🏠 **Lokal zuerst:** Viele Skills laufen komplett auf dem eigenen Rechner, Daten liegen in SQLite statt in der Cloud.
- 🔐 **Keine Schlüssel im Code:** API-Keys und Zugangsdaten kommen aus einer `.env`, die per `.gitignore` nie im Repo landet.
- 🇩🇪 **Deutsch im Alltag:** Spracheingaben wie *„12,50 € bei Rewe“* oder *„Termin morgen 14 Uhr“* funktionieren direkt.
- 🤖 **Für Agenten gebaut:** Jede `SKILL.md` sagt dem Agenten, wann und wie er den Skill nutzt.

**Legende:** 🏠 läuft lokal · 🌐 öffentlicher Online-Dienst, kein Key · 🔑 API-Key oder Zugang nötig

---

## 📋 Alle Skills im Überblick

### 🎧 Audio, Sprache & Video
| Skill | Beschreibung | Betrieb |
|---|---|:---:|
| 🎙️ [audio-transcription](#audio-transcription) | Audio zu Text mit faster-whisper (MP3, OGG, WAV …) | 🏠 |
| 🗣️ [piper-tts](#piper-tts) | Deutsche Sprachausgabe mit der Thorsten-Stimme | 🏠 |
| 🔊 [elevenlabs-tts](#elevenlabs-tts) | Hochwertige Sprachausgabe, auch mit geklonten Stimmen | 🔑 |
| 📺 [superdata-youtube-transcript](#superdata-youtube-transcript) | YouTube-Transkripte und KI-Zusammenfassungen | 🔑 |

### 🎨 Bild & Spaß
| Skill | Beschreibung | Betrieb |
|---|---|:---:|
| 🖼️ [image-generation](#image-generation) | Kostenlose Bildgenerierung via Pollinations.ai | 🌐 |
| 🎨 [leonardo-image-gen](#leonardo-image-gen) | Leonardo AI (FLUX, Lucid, XL) mit Pollinations-Fallback | 🔑 |
| 😂 [meme-architect](#meme-architect) | Memes passend zum Kontext über imgflip | 🔑 |

### 💶 Finanzen
| Skill | Beschreibung | Betrieb |
|---|---|:---:|
| 💰 [expense-tracker](#expense-tracker) | Budget mit Einkommen, Fixkosten und Ersparnissen, per Spracheingabe | 🏠 |
| ₿ [crypto-tracker](#crypto-tracker) | Kurse und Gewinn/Verlust für BTC und XRP via CoinGecko | 🌐 |

### 📅 Produktivität & Lernen
| Skill | Beschreibung | Betrieb |
|---|---|:---:|
| 📅 [calendar](#calendar) | Lokaler Kalender mit natürlicher Spracheingabe und Erinnerungen | 🏠 |
| ✉️ [email-sender](#email-sender) | E-Mails senden und lesen (SMTP/IMAP: Web.de, Gmail, GMX …) | 🔑 |
| 🎓 [ap1-training-tracker](#ap1-training-tracker) | IHK-AP1-Training für Fachinformatiker mit 280 Fragen | 🏠 |

### 📦 Tracking & Monitoring
| Skill | Beschreibung | Betrieb |
|---|---|:---:|
| 📦 [package-tracking](#package-tracking) | Pakete von DHL, Hermes und GLS an einem Ort (DPD in Planung) | 🌐 |
| 📡 [vodafone-sender-monitor](#vodafone-sender-monitor) | Vodafone-Kabel-Senderlisten überwachen, Enigma2-Export | 🌐 |
| 🏃 [sports-tracker](#sports-tracker) | Training, Kalorien und Workouts (P90X, Rad, Laufen, Komoot-Import) | 🏠 |

### 🛠️ Entwicklung & Betrieb
| Skill | Beschreibung | Betrieb |
|---|---|:---:|
| 🐙 [github-manager](#github-manager) | Skills auf GitHub veröffentlichen und synchron halten | 🔑 |
| 💻 [mammouth-coding](#mammouth-coding) | Code-Generierung über Mammouth.ai | 🔑 |
| 📝 [wordpress-manager](#wordpress-manager) | WordPress-Beiträge per REST API verwalten | 🔑 |
| ☁️ [mega-filehoster](#mega-filehoster) | MEGA.nz: Upload, Download, Share-Links | 🔑 |
| 💾 [backup-manager](#backup-manager) | Git- und SQLite-Backups des Workspace mit Rotation | 🏠 |

---

## 🚀 Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/James-Butler2026/openclaw-skills.git
cd openclaw-skills

# 2. Gewünschten Skill in den OpenClaw-Workspace kopieren
cp -r audio-transcription ~/.openclaw/workspace/skills/

# 3. Setup-Anleitung lesen (Abhängigkeiten, .env-Variablen)
cat audio-transcription/SKILL.md
```

**Voraussetzungen**
- 🐍 Python 3.8+
- 🦞 OpenClaw-Workspace (empfohlen, die Skills laufen aber auch einzeln)
- 🔑 `.env` im Workspace-Root mit den Keys der 🔑-Skills

---

## 📦 Skills im Detail

<details id="audio-transcription">
<summary><b>🎙️ audio-transcription</b> – Audio zu Text mit faster-whisper</summary>

- Unterstützt MP3, OGG, WAV und weitere Formate
- Modelle von `tiny` bis `large-v3`
- Sprache automatisch erkennen oder fest vorgeben, Deutsch nativ

```bash
python3 scripts/transcribe.py audio.mp3 --language de
```

→ [Details ansehen](audio-transcription/README.md)
</details>

<details id="piper-tts">
<summary><b>🗣️ piper-tts</b> – Deutsche Sprachausgabe, lokal</summary>

- Thorsten-Stimme (deutsch, männlich)
- Kein API-Key, läuft lokal
- Kann direkt als Telegram-Sprachnachricht senden

```bash
python3 scripts/piper_tts.py "Hallo Welt" --send
```

→ [Details ansehen](piper-tts/README.md)
</details>

<details id="elevenlabs-tts">
<summary><b>🔊 elevenlabs-tts</b> – Sprachausgabe über ElevenLabs</summary>

- 70+ Sprachen, sehr gute deutsche Aussprache
- Modelle: `multilingual_v2`, `turbo`, `flash`
- Eigene geklonte Stimmen, Streaming

```bash
python3 scripts/elevenlabs_tts.py speak "Hallo Welt" --voice VOICE_ID
```

→ [Details ansehen](elevenlabs-tts/README.md)
</details>

<details id="superdata-youtube-transcript">
<summary><b>📺 superdata-youtube-transcript</b> – YouTube-Transkripte mit Supadata</summary>

- Supadata API (100 Credits/Monat kostenlos)
- KI-Zusammenfassungen
- 30-Tage-Cache, Credits werden nur bei Erfolg verbraucht

```python
from scripts.youtube_transcript_superdata import get_transcript_summary
result = get_transcript_summary(video_id="...")
```

→ [Details ansehen](superdata-youtube-transcript/README.md)
</details>

<details id="image-generation">
<summary><b>🖼️ image-generation</b> – Kostenlose Bilder via Pollinations.ai</summary>

- Kein API-Key nötig, keine bekannten Rate-Limits
- Eigene Größen und Seeds
- Ohne Wasserzeichen

```bash
python3 scripts/generate_image.py "A beautiful sunset" --width 1024 --height 768
```

→ [Details ansehen](image-generation/README.md)
</details>

<details id="leonardo-image-gen">
<summary><b>🎨 leonardo-image-gen</b> – Leonardo AI mit Pollinations-Fallback</summary>

- Leonardo AI API (tägliche Credits)
- Modelle: FLUX.1, Lucid, Leonardo XL
- Fällt automatisch auf Pollinations zurück

```bash
python3 scripts/leonardo_generate.py "Ein elegantes Maskenstück" --model flux-schnell
```

→ [Details ansehen](leonardo-image-gen/README.md)
</details>

<details id="meme-architect">
<summary><b>😂 meme-architect</b> – Memes mit der imgflip API</summary>

- Erstellt Memes automatisch aus dem Gesprächskontext
- Nutzt die imgflip-Vorlagen
- Erkennt die Stimmung und wählt passende Vorlagen

```bash
python3 scripts/meme_architect.py "lustiger Moment"
```

→ [Details ansehen](meme-architect/README.md)
</details>

<details id="expense-tracker">
<summary><b>💰 expense-tracker</b> – Budget mit Einkommen, Fixkosten und Ersparnissen (v3.0)</summary>

- 🎤 Spracheingabe: *„Habe 12,50 € bei Rewe ausgegeben“*
- 📊 Einkommen – Fixkosten – Variabel = Ersparnisse
- 📅 ISO-KW (Mo–So) und Monatswochen (1.–7., 8.–14. …)
- ⏱️ Befristete Fixkosten mit Enddatum
- 🔢 Cent-genau, ohne Rundung
- 🗓️ Monats-, Jahres- und Gesamtübersicht

```bash
python3 scripts/expense_tracker.py "12,50€ bei Rewe"
python3 scripts/expense_tracker.py --weekly          # diese Woche (Mo–So)
python3 scripts/expense_tracker.py --last-week       # letzte Woche
python3 scripts/expense_tracker.py --month-to-date   # 1. bis heute
python3 scripts/expense_tracker.py --monthly         # Budget-Bericht
python3 scripts/expense_tracker.py --year            # Jahresübersicht
python3 scripts/expense_tracker.py --total           # Gesamtübersicht
```

→ [Details ansehen](expense-tracker/README.md)
</details>

<details id="crypto-tracker">
<summary><b>₿ crypto-tracker</b> – Krypto-Portfolio für BTC und XRP</summary>

- Aktuelle Kurse in USD/EUR via CoinGecko
- Gewinn/Verlust und 24-h-Änderung
- Stop-Loss bei −20 %, Take-Profit bei +25 %

```bash
python3 scripts/bison_tracker.py --init
python3 scripts/bison_tracker.py --status
```

→ [Details ansehen](crypto-tracker/README.md)
</details>

<details id="calendar">
<summary><b>📅 calendar</b> – Lokaler Kalender mit Spracheingabe</summary>

- Natürliche Sprache: *„Termin morgen 14 Uhr“*
- Geburtstage mit jährlicher Erinnerung
- Wiederholungen: täglich, wöchentlich, monatlich, jährlich
- Erinnerungen per Cron

```bash
python3 scripts/calendar_cli.py "Termin morgen 14 Uhr beim Zahnarzt"
python3 scripts/calendar_cli.py --today
```

→ [Details ansehen](calendar/README.md)
</details>

<details id="email-sender">
<summary><b>✉️ email-sender</b> – E-Mails senden und lesen</summary>

- Web.de, Gmail (App-Passwort), GMX oder eigener Server
- Text, HTML, Anhänge, CC/BCC
- Postfach lesen per IMAP

```bash
python3 scripts/send_email.py --to empfaenger@example.com \
    --subject "Hallo" --body "Testnachricht"
```

→ [Details ansehen](email-sender/README.md)
</details>

<details id="ap1-training-tracker">
<summary><b>🎓 ap1-training-tracker</b> – IHK AP1 für Fachinformatiker</summary>

- 280 Fragen aus dem Prüfungsstoff, davon 50 zu Subnetting
- Interaktives Training mit Feedback
- Statistiken und Fortschritt in SQLite

```bash
python3 scripts/ap1_training.py
python3 scripts/ap1_tracker.py --daily
```

→ [Details ansehen](ap1-training-tracker/README.md)
</details>

<details id="package-tracking">
<summary><b>📦 package-tracking</b> – DHL, Hermes und GLS an einem Ort</summary>

| Carrier | Methode | API-Key | Dauer | Status |
|---|---|:---:|:---:|:---:|
| 🚚 DHL | REST API (öffentlich) | ❌ | ~2 s | ✅ |
| 📦 Hermes | Browser + OCR | ❌ | ~30 s | ✅ |
| 🔵 GLS | REST API (öffentlich) | ❌ | ~2 s | ✅ |
| ⚪ DPD | offen | ❓ | – | 🧪 Test ausstehend |

- Ein Manager für alle Pakete, Verlauf in SQLite
- Automatische Prüfung um 10:00 und 16:00 Uhr
- Telegram-Meldung bei Statusänderung

```bash
python3 scripts/package_manager.py add -c [CODE] -r dhl -d "Beschreibung"
python3 scripts/package_manager.py track --json    # alle Pakete prüfen
python3 scripts/package_manager.py list            # Übersicht
```

**Aufbau:** `package_manager.py` (Koordination, DB) · `dhl_tracker.py` · `hermes_tracker.py` · `gls_tracker.py` · `package_tracking_agent.py` (OpenClaw-Agent)

→ [Details ansehen](package-tracking/SKILL.md)
</details>

<details id="vodafone-sender-monitor">
<summary><b>📡 vodafone-sender-monitor</b> – Senderlisten im Blick</summary>

- Enigma2-Export der Vodafone-Kabel-Senderlisten
- 🔔 Meldung bei neuen Sendern
- 🔄 Wöchentlicher Scan (samstags 20:00 Uhr), Daten in SQLite

```bash
python3 scripts/vodafone_monitor.py --init
python3 scripts/vodafone_monitor.py --scan
```

→ [Details ansehen](vodafone-sender-monitor/README.md)
</details>

<details id="sports-tracker">
<summary><b>🏃 sports-tracker</b> – Training und Kalorien</summary>

- Aktivitäten: Spazieren, Rad, Wandern, Laufen, P90X
- 🔥 Kalorien nach MET-Werten, mit eigenem Körpergewicht
- 💪 Workouts als erledigt/verpasst markieren
- 📊 Wochen- und Monatsberichte, Komoot-Import
- 🎯 Sarkasmus-Modus bei verpassten Trainingstagen

```bash
python3 scripts/sports_tracker.py --add "5 km Spazieren"
python3 scripts/sports_tracker.py --done     # P90X erledigt
python3 scripts/sports_tracker.py --week     # Wochenbericht
```

→ [Details ansehen](sports-tracker/README.md)
</details>

<details id="github-manager">
<summary><b>🐙 github-manager</b> – Skills auf GitHub veröffentlichen</summary>

- Repositories anlegen
- Einzelne oder alle Skills synchronisieren
- README automatisch erzeugen, GitHub Actions

```bash
python3 scripts/github_publish.py --skill image-generation --repo openclaw-skills
```

→ [Details ansehen](github-manager/README.md)
</details>

<details id="mammouth-coding">
<summary><b>💻 mammouth-coding</b> – Code-Generierung über Mammouth.ai</summary>

- Nur für Code-Generierung gedacht
- Wiederholversuche mit Exponential Backoff
- Saubere Fehlerbehandlung

```bash
python3 scripts/mammouth_coder.py "Erstelle eine Python-Klasse für..."
```

→ [Details ansehen](mammouth-coding/README.md)
</details>

<details id="wordpress-manager">
<summary><b>📝 wordpress-manager</b> – WordPress per REST API</summary>

- Beiträge erstellen, bearbeiten, löschen
- Kategorien und Tags
- Cloudflare-kompatibel, mit Retry-Logik

```bash
python3 wordpress_manager.py --create "Titel" "HTML-Inhalt"
```

→ [Details ansehen](wordpress-manager/README.md)
</details>

<details id="mega-filehoster">
<summary><b>☁️ mega-filehoster</b> – MEGA.nz verwalten</summary>

- Dateien hoch- und herunterladen
- Ordner auflisten, Share-Links erzeugen
- Freien Speicher prüfen

```bash
python3 scripts/mega_manager.py upload /pfad/zur/datei.txt
```

→ [Details ansehen](mega-filehoster/README.md)
</details>

<details id="backup-manager">
<summary><b>💾 backup-manager</b> – Git- und SQLite-Backups des Workspace</summary>

- Git-Commit aller Änderungen, automatisch nach Bereich sortiert (agents, scripts, skills, docs …)
- SQLite-Backups mit Zeitstempel, behält die letzten 7
- Einmalig, als Daemon oder täglich per Cron (03:00 Uhr), optional mit Push

```bash
python3 scripts/git_backup.py --once           # Git + SQLite
python3 scripts/git_backup.py --once --push    # mit Push zum Remote
python3 scripts/git_backup.py --status
```

→ [Details ansehen](backup-manager/README.md)
</details>

---

## ⚙️ Konfiguration

Die 🔑-Skills lesen ihre Keys aus einer `.env` im OpenClaw-Workspace. Welche Variablen ein Skill braucht, steht in seiner `SKILL.md` bzw. `README.md`.

```
~/.openclaw/workspace/
├── .env              # API-Keys und Zugangsdaten (nie committen)
├── skills/
│   ├── audio-transcription/
│   ├── package-tracking/
│   └── ...
├── scripts/          # Skill-Skripte
└── data/             # Datenbanken, Caches
```

> [!IMPORTANT]
> `.env`, Datenbanken (`*.db`), Logs und `memory/` stehen in der `.gitignore`. Bitte keine Keys in Skripte oder READMEs schreiben.

---

## 🤝 Mitwirken

Die Sammlung wächst laufend. Ideen, Fehlermeldungen und Pull Requests sind willkommen: einfach ein [Issue](https://github.com/James-Butler2026/openclaw-skills/issues) aufmachen.

## 📜 Lizenz

Alle Skills sind unter der [MIT-Lizenz](LICENSE) veröffentlicht.

<div align="center">
<sub>Gebaut mit 🦞 OpenClaw und viel ☕</sub>
</div>
