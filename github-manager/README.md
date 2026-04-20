# GitHub Manager Skill

Skills zu GitHub veröffentlichen und Repository verwalten.

## Features

- 🐙 Repository erstellen
- 🔄 Skills zu GitHub pushen
- 📁 Automatische README-Generierung
- 🏷️ Versionierung

## Installation

```bash
cd ~/.openclaw/workspace/skills/github-manager/
```

## Verwendung

```bash
# Einzelnen Skill veröffentlichen
python3 scripts/github_publish.py \
    --skill image-generation \
    --repo openclaw-skills

# Mit Beschreibung
python3 scripts/github_publish.py \
    --skill piper-tts \
    --repo openclaw-skills \
    --description "German TTS with Thorsten voice"
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=dein_username
GITHUB_EMAIL=deine_email@example.com
```

**Token erstellen:** https://github.com/settings/tokens

## Sicherheit

- **WICHTIG:** GitHub Token niemals committen!
- **WICHTIG:** Token hat repo-Zugriff – sicher aufbewahren!
- Bei Verdacht auf Leak: Token sofort revoken

---
*GitHub-Verwaltung für OpenClaw* 🐙
