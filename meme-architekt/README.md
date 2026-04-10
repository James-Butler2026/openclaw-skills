# 🎨 Context-Aware Meme Architect

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Ein intelligenter Meme-Generator, der Gesprächskontext analysiert und passende Memes über die imgflip API erstellt.

![Meme Example](https://i.imgflip.com/aou2sd.jpg)

## ✨ Features

- 🎭 **Automatische Emotionserkennung** – Wählt das perfekte Template basierend auf Kontext
- 📝 **KI-generierte Texte** – Erstellt passenden Ober-/Untertext
- 🖼️ **Echte Meme-Templates** – Via imgflip API (keine lokalen Bilder nötig)
- 🎯 **8+ Templates** – Von Success Kid bis Crying Wolverine
- ⚡ **Schnell & einfach** – Direkte API-Integration

## 🚀 Installation

### Voraussetzungen

- Python 3.8+
- imgflip Account (kostenlos)

### Schritt 1: Abhängigkeiten installieren

```bash
pip install Pillow
```

### Schritt 2: imgflip Account erstellen

1. Gehe zu [imgflip.com/signup](https://imgflip.com/signup)
2. Erstelle einen kostenlosen Account
3. Notiere Username und Passwort

### Schritt 3: Konfiguration

Füge zu deiner `.env` Datei hinzu:

```bash
IMGFLIP_USERNAME=dein_username
IMGFLIP_PASSWORD=dein_passwort
```

Die `.env` Datei sollte bereits existieren (von anderen Skills). Falls nicht, erstelle sie im Projekt-Root.

## 📖 Nutzung

### CLI

```bash
# Basis-Nutzung
python3 scripts/meme_architect.py "Mein Text hier"

# Mit spezifischer Emotion
python3 scripts/meme_architect.py "Text" --emotion success

# Alle Templates anzeigen
python3 scripts/meme_architect.py --list

# Demo-Modus (4 Beispiele)
python3 scripts/meme_architect.py --demo
```

### Python API

```python
from scripts.meme_architect import create_context_meme

# Erstelle Meme aus Kontext
result = create_context_meme(
    context="Endlich läuft der Cron-Job nach 3 Tagen",
    emotion="success"  # Optional
)

print(f"Meme erstellt: {result}")
# Output: /tmp/meme_architect/meme_20260410_094838.png
```

## 🎭 Verfügbare Templates

| Emotion | Template | ID | Beispiel-Text |
|---------|----------|-----|---------------|
| `success` | Success Kid | 61544 | "Endlich... / Es funktioniert!" |
| `frustration` | This Is Fine | 55311130 | "Alles läuft / (nicht)" |
| `dilemma` | Two Buttons | 87743020 | "Schlafen / Cron-Job bauen" |
| `superiority` | Drake Pointing | 181913649 | "Manuell / Automatisieren" |
| `irony` | Distracted Boyfriend | 112126428 | "Nur ein kleiner Fix / *baut 47 Skills*" |
| `nostalgia` | Crying Wolverine | 91538330 | "Erinnert sich an / Nur 5 Cron-Jobs" |

## 🏗️ Wie es funktioniert

1. **Input:** Nutzer gibt Text ein (z.B. "Pollinations streikt wieder")
2. **Analyse:** Skill erkennt Emotion anhand von Keywords ("streikt" → `frustration` oder `irony`)
3. **Template:** Wählt passendes imgflip Template (z.B. "This Is Fine")
4. **Text:** Generiert Ober-/Untertext passend zur Emotion
5. **API:** Ruft imgflip API mit curl auf
6. **Ausgabe:** Lädt Bild herunter und gibt Dateipfad zurück

## 📂 Projektstruktur

```
meme-architect/
├── README.md                 # Diese Datei
├── SKILL.md                  # Detaillierte Skill-Dokumentation
├── scripts/
│   └── meme_architect.py     # Hauptskript
└── references/
    └── imgflip-api.md        # API-Referenz
```

## 🔧 Entwicklung

### Lokale Tests

```bash
# Teste Emotionserkennung
python3 scripts/meme_architect.py --demo

# Teste spezifisches Template
python3 scripts/meme_architect.py "Test Text" --emotion success
```

### Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Keine Credentials" | `.env` erstellen mit `IMGFLIP_USERNAME` und `IMGFLIP_PASSWORD` |
| "Pillow nicht gefunden" | `pip install Pillow` ausführen |
| "403 Forbidden" | Normal bei urllib, curl-Implementierung funktioniert |

## 🤝 Mitwirken

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📜 Lizenz

Verteilt unter der MIT License. Siehe `LICENSE` für mehr Informationen.

## 🎩 Credits

Erstellt mit ❤️ von James, dem digitalen Butler.

*"Wenn eine API streikt, bauen wir einfach unsere eigene Lösung."*

---

**🌟 Star das Repo wenn es dir gefällt!**
