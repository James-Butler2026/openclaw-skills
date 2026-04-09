---
name: meme-architect
description: Context-Aware Meme Generator - Analysiert Text/Nachrichten und erstellt passende Memes mit imgflip API. Perfekt für humorvolle Antworten im Chat.
---

# Context-Aware Meme Architect 🎭

Ein intelligenter Meme-Generator, der Kontext versteht und passende Memes erstellt.

## Features

- 🧠 **KI-gestützte Textanalyse** - Versteht Stimmung und Kontext
- 🎨 **Auto-Template-Auswahl** - Wählt passendes Meme-Template automatisch
- ⚡ **Schnelle Generierung** - Direkter Upload zu Imgflip oder lokale Erstellung
- 😂 **Humorvoll** - Perfekt für Chat-Antworten und interne Witze

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/James-Butler2026/openclaw-skills.git
cd openclaw-skills/meme-architect
```

### 2. Python-Abhängigkeiten installieren

```bash
pip install Pillow requests
```

### 3. Optional: imgflip Account

Für Template-Upload und direkte Links:
- https://imgflip.com/signup
- Username/Passwort in `.env` speichern:

```bash
IMGFLIP_USERNAME=dein_username
IMGFLIP_PASSWORD=dein_passwort
```

## Nutzung

### Direkt im Chat

```bash
# Einfacher Text
python3 scripts/meme_architect.py "Mein Code kompiliert endlich!"

# Mit Kontext
python3 scripts/meme_architect.py "Nach 3 Stunden Debugging... es war nur ein Semikolon"

# Spezifisches Template erzwingen
python3 scripts/meme_architect.py "Wenn der Code endlich läuft" --template "success-kid"
```

### Als OpenClaw Skill

```bash
# Automatische Template-Auswahl
meme "Der Server ist wieder online"

# Mit spezifischem Template
meme "Feature Request um 17:55 Uhr" --template "two-buttons"
```

## Verfügbare Templates

| Template | ID | Wann verwenden |
|----------|-----|----------------|
| Success Kid | 61544 | Erfolge, kleine Siege |
| Distracted Boyfriend | 112126428 | Ablenkung, neue Prioritäten |
| Two Buttons | 87743020 | Schwierige Entscheidungen |
| Drake Hotline Bling | 181913649 | Ablehnung vs. Zustimmung |
| Change My Mind | 129242436 | Kontroverse Meinungen |
| Expanding Brain | 93895088 | Eskalation, Erkenntnisse |
| Roll Safe | 89370399 | Schlaue Lösungen |
| Mocking Spongebob | 102156234 | Spott, Sarkasmus |
| Woman Yelling at Cat | 188390779 | Konflikte, Missverständnisse |
| Always Has Been | 216951317 | Offensichtlichkeiten |

## Technische Details

- **Template-Auswahl:** Keywords + Sentiment Analysis
- **Text-Positionierung:** Automatisch oben/unten
- **Schriftart:** Impact (klassische Meme-Schrift)
- **Ausgabe:** Lokale PNG oder imgflip-Link

## Beispiele

### Input: "Der Build war erfolgreich"
→ **Template:** Success Kid
→ **Text:** "BUILD ERFOLGREICH" / "ICH BIN EIN GOTT"

### Input: "Wenn du einen Bug findest aber 10 neue erstellst"
→ **Template:** Roll Safe
→ **Text:** "KANN KEINE BUGS HABEN" / "WENN MAN KEINEN CODE SCHREIBT"

### Input: "Feature Request um 17:55 Uhr"
→ **Template:** Two Buttons
→ **Text:** "NOCH HEUTE IMPLEMENTIEREN" / "ERST MORGEN ANSCHAUEN"

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| "Template nicht gefunden" | Template-ID prüfen oder --auto verwenden |
| Text zu lang | Automatische Kürzung oder manuelle Anpassung |
| Bild zu klein | `--quality high` für größere Ausgabe |

---

*Für den perfekten Moment im Chat* 😂🎩
