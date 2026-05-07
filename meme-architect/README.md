# 🎨 Context-Aware Meme Architect

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Ein intelligenter Meme-Generator, der Gesprächskontext analysiert und automatisch das passende Template via imgflip API sucht.

![Meme Example](https://i.imgflip.com/ar50md.jpg)

## ✨ Features

- 🤖 **Auto-Modus** – Kontext rein, Meme raus (Keywords → Template-Suche → Erstellung)
- 🎭 **Emotionserkennung** – Analysiert Text (success, frustration, irony, etc.)
- 🔑 **Keyword-basierte Template-Suche** – 14 Kategorien (Schule, Arbeit, Sport, Schmerz, etc.)
- 🎯 **10+ Templates** – Inkl. Hide the Pain Harold, Sleeping Shaq, Success Kid uvm.
- ⚡ **imgflip API via curl** – Zuverlässig und schnell

## 🚀 Installation

### Voraussetzungen

1. Python 3.8+
2. imgflip Account (kostenlos): https://imgflip.com/signup

### Konfiguration

Erstelle `.env` im Projekt-Root:

```bash
IMGFLIP_USERNAME=dein_username
IMGFLIP_PASSWORD=dein_passwort
```

## 📖 Nutzung

### Auto-Modus (empfohlen)

```bash
python3 scripts/meme_architect.py --auto "P90X wieder angefangen, bin total kaputt"
# → Findet automatisch "Hide the Pain Harold" via "kaputt/schmerzen"-Keywords
```

### Weitere Modi

```bash
# Manuell mit Emotion
python3 scripts/meme_architect.py "Text" --emotion irony

# Templates durchsuchen
python3 scripts/meme_architect.py --search "sleeping"

# Direkt mit ID
python3 scripts/meme_architect.py --create 27813981 "Oben" "Unten"

# Alle Templates anzeigen
python3 scripts/meme_architect.py --list
```

### Python API

```python
from scripts.meme_architect import create_auto_meme

result = create_auto_meme(
    context="Hab Training wieder angefangen, bin kaputt",
    emotion="frustration"  # Optional
)
# Output: /tmp/meme_architect/meme_20260507_083600.png
```

## 🎭 Emotions-Trigger

| Emotion | Trigger-Wörter |
|---------|---------------|
| `success` | funktioniert, geschafft, endlich, läuft, done |
| `frustration` | fehler, nicht, kaputt, bug, scheiße |
| `irony` | toll, super + negatives Wort |
| `dilemma` | oder, vs, entscheiden |
| `superiority` | besser, nein, upgrade |
| `nostalgia` | früher, damals, erinnerst |

## 🔑 Keyword-Kategorien

| Kategorie | Beispiel-Trigger | Matcht auf |
|-----------|-----------------|-----------|
| `sleeping` | müde, pennen, tired | Sleeping Shaq, etc. |
| `studying` | schule, prüfung, unterricht | Studying-Templates |
| `pain` | kaputt, schmerzen, dead | **Hide the Pain Harold** |
| `work` | arbeit, job, büro | Work-Templates |
| `gym` | sport, fitness, gym | Gym/Exercise |
| `computer` | pc, code, server, bug | Nerd-Templates |
| `food` | essen, hunger, pizza | Food-Templates |
| & mehr | Auto, Beziehung, Tier, Gaming... | |

## ⚡ Technik

### Warum curl statt Python?

```bash
# ❌ Python urllib/requests → 403 Forbidden
# ✅ curl mit User-Agent → funktioniert
```

Der Skill verwendet `subprocess.run(["curl", ...])` mit `User-Agent: Mozilla/5.0...`.

### Auto-Modus Workflow

```
Input → Emotion erkennen → Keywords extrahieren
    → imgflip API (Top 100) → Template-ID → Meme erstellen
```

## 📂 Projektstruktur

```
meme-architect/
├── README.md                 # Diese Datei
├── SKILL.md                  # Detaillierte Skill-Doku
├── scripts/
│   └── meme_architect.py     # Hauptskript (gesäubert!)
└── references/
    └── imgflip-api.md        # API-Referenz
```

## 🐛 Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "This Is Fine" statt passendem Template | `--create ID "O" "U"` für direktes Template |
| 403 Forbidden | Immer curl verwenden |
| Kein Treffer in Top 100 | ID manuell via --create |
| Keine Credentials | `.env` prüfen |

## 📜 Lizenz

MIT License.

## 🎩 Credits

Erstellt mit ❤️ von James, dem digitalen Butler.

---

**GitHub:** https://github.com/James-Butler2026/openclaw-skills/tree/main/meme-architect
