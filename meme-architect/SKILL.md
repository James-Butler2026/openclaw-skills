---
name: meme-architect
description: |
  Context-Aware Meme Architect – Ein KI-Agent, der Gespräche, Texte und News 
  in passende Memes verwandelt. Nutzt die imgflip API für echte Meme-Templates 
  mit automatischer Emotionserkennung, Keyword-basierter Template-Suche und Text-Generierung.
  
  Use when:
  1. Jemand einen lustigen Moment aus einer Konversation meme-n will
  2. Ein Erfolg/Misserfolg meme-würdig ist
  3. Automatische Meme-Generierung aus Chat-Kontext gewünscht ist
---

# 🎨 Context-Aware Meme Architect

Ein intelligenter Meme-Generator, der Gesprächskontext analysiert und automatisch das passende Template via imgflip API sucht.

## ✨ Features

- **🎭 Emotionserkennung** – Analysiert Text und erkennt Emotion (success, frustration, irony, etc.)
- **🔑 Keyword-basierte Template-Suche** – Extrahiert Themen aus Kontext (Schule, Arbeit, Sport, etc.) und matcht mit imgflip Top 100
- **📝 Kontext-basierte Texte** – Generiert automatisch Ober-/Untertext
- **🤖 Auto-Modus** – Ein Befehl: Kontext rein, Meme raus
- **🎯 10+ Templates** – Inkl. Hide the Pain Harold, Sleeping Shaq, Success Kid uvm.
- **⚡ imgflip API via curl** – Kein Python-urllib (wird blockiert)

## 🚀 Schnellstart

### Voraussetzungen

1. **imgflip Account erstellen:** https://imgflip.com/signup
2. **.env konfigurieren:**
   ```bash
   IMGFLIP_USERNAME=dein_username
   IMGFLIP_PASSWORD=dein_passwort
   ```

### Nutzung

```bash
# 🤖 AUTO-MODUS (empfohlen)
python3 skills/meme-architect/scripts/meme_architect.py --auto "3 Monate Schule, heute Prüfung, nichts verstanden"

# Manuell mit Emotion
python3 meme_architect.py "Text" --emotion irony

# Templates suchen
python3 meme_architect.py --search "sleeping"

# Mit bestimmter ID
python3 meme_architect.py --create 27813981 "Oben" "Unten"
```

## 🎭 Emotionserkennung

| Emotion | Typische Trigger |
|---------|-----------------|
| `success` | funktioniert, geschafft, endlich, läuft, done |
| `frustration` | fehler, nicht, kaputt, bug, scheiße |
| `dilemma` | oder, vs, entscheiden, dilemma |
| `superiority` | besser, nein, upgrade, baut |
| `irony` | toll, super, perfekt (+ negatives Wort) |
| `nostalgia` | früher, damals, erinnerst, alte zeiten |

## 🔑 Keyword-Kategorien

| Kategorie | Trigger-Wörter | Template-Suche |
|-----------|---------------|----------------|
| `sleeping` | schlaf, müde, pennen, tired | sleeping |
| `studying` | schule, lernen, prüfung, unterricht | studying |
| `pain` | kaputt, schmerzen, erschöpft, dead | pain hide the pain harold |
| `work` | arbeit, job, büro | work |
| `computer` | pc, server, code, bug | computer nerd |
| `food` | essen, pizza, hunger | food |
| `gym` | sport, fitness, workout | gym |
| `driving` | auto, fahren, verkehr | driving |
| ... und 6 weitere | | |

**So funktioniert's:** Der Skill extrahiert Keywords aus deinem Text (z.B. "kaputt" + "training" → `pain` + `gym`), durchsucht die imgflip Top 100 nach passenden Template-Namen und wählt das beste.

## 🔧 Technische Details

### Warum curl?

**imgflip blockiert Python's urllib/requests!**
- ❌ `urllib.request.urlopen()` → 403 Forbidden
- ✅ `curl` mit User-Agent → funktioniert

### Auto-Modus vs. Manuell

| Modus | Befehl | Template-Suche | Am besten für |
|-------|--------|---------------|--------------|
| Auto | `--auto "..."` | Keyword-Matching + API | Alltag, Chat-Kontext |
| Manuell | `--emotion irony` | Feste Emotion | Kontrolle |
| Direkt | `--create ID "O" "U"` | Eigene ID | Spezial-Templates |
| Suche | `--search "begriff"` | Top 100 durchsuchen | Template finden |

### Neue Templates (Top 100 Found)

| Name | ID | Gefunden via |
|------|-----|-------------|
| Hide the Pain Harold | 27813981 | `pain`-Keyword |
| Sleeping Shaq | 99683372 | `sleeping`-Keyword |
| Soldier protecting sleeping child | 171305372 | `sleeping`-Keyword |

## 🐛 Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| Keine Credentials | `.env` prüfen |
| "This Is Fine" bei P90X | Keyword `kaputt`/`schmerzen` fehlt ggf. → manuell `--create 27813981` |
| 403 Forbidden | Immer curl verwenden |
| Template nicht gefunden | Nicht in Top 100 → ID direkt via `--create` |
| Pillow fehlt | `pip install Pillow` (nur Fallback) |

---

**GitHub:** https://github.com/James-Butler2026/openclaw-skills/tree/main/meme-architect
