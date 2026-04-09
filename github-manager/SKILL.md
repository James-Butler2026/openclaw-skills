---
name: github-manager
description: Manage GitHub repositories, sync skills to GitHub, create repos, push updates. Use when the user wants to publish skills to GitHub, manage repositories, sync workspace to remote GitHub account, or automate GitHub workflows.
---

# GitHub Manager Skill

Verwaltet GitHub-Repositories und synchronisiert Skills automatisch. Perfekt für Backup und Veröffentlichung.

## Features

- 🐙 **Repository erstellen** – Neue Repos für Skills
- 🔄 **Auto-Sync** – Skills zu GitHub pushen
- 📁 **Skill-Export** – Ordnerstruktur vorbereiten
- 🏷️ **Versionierung** – Tags und Releases
- 📖 **README-Generierung** – Automatische Dokumentation

## Voraussetzungen

### 1. GitHub Account
- Account erstellen: https://github.com/join
- E-Mail bestätigen (Code wurde an j_butler@web.de gesendet)

### 2. Personal Access Token (PAT)

Erstelle einen Token unter: https://github.com/settings/tokens

**Berechtigungen:**
- ✅ `repo` – Repository-Zugriff
- ✅ `workflow` – GitHub Actions
- ✅ `write:packages` – Packages schreiben

### 3. Token in .env eintragen

```bash
# In ~/.openclaw/workspace/.env eintragen:
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=dein_username
GITHUB_EMAIL=j_butler@web.de
```

## Schnellstart

### Skill zu GitHub veröffentlichen
```bash
# Einzelnen Skill veröffentlichen
python3 skills/github-manager/scripts/github_publish.py \
    --skill image-generation \
    --repo openclaw-skills

# Mit Beschreibung
python3 skills/github-manager/scripts/github_publish.py \
    --skill piper-tts \
    --repo openclaw-skills \
    --description "German TTS with Thorsten voice"
```

### Alle Skills synchronisieren
```bash
# Alle Skills auf einmal
python3 skills/github-manager/scripts/github_publish.py \
    --all \
    --repo openclaw-skills
```

### Repository erstellen
```bash
# Neues Repo anlegen
python3 skills/github-manager/scripts/github_publish.py \
    --create-repo openclaw-skills \
    --private false \
    --description "OpenClaw Skill Collection"
```

## Parameter

| Parameter | Kurzform | Beschreibung |
|-----------|----------|--------------|
| `--skill` | `-s` | Skill-Name zu veröffentlichen |
| `--repo` | `-r` | Ziel-Repository |
| `--all` | `-a` | Alle Skills veröffentlichen |
| `--create-repo` | `-c` | Neues Repository erstellen |
| `--description` | `-d` | Repository-Beschreibung |
| `--private` | `-p` | Privates Repository (true/false) |

## Veröffentlichungs-Workflow

### 1. Skill vorbereiten
```bash
# Skill-Ordner prüfen
ls -la skills/image-generation/

# Sollte enthalten:
# - SKILL.md (Dokumentation)
# - scripts/ (Code)
# - README.md (optional)
```

### 2. Zu GitHub pushen
```bash
python3 skills/github-manager/scripts/github_publish.py \
    --skill image-generation \
    --repo openclaw-skills \
    --description "Free image generation via Pollinations.ai"
```

### 3. README wird automatisch generiert
Das Script erstellt:
- `README.md` aus SKILL.md
- `LICENSE` (MIT)
- `.gitignore`
- GitHub Actions (optional)

## Python API

```python
from skills.github_manager.scripts.github_publish import publish_skill, create_repo

# Repository erstellen
create_repo(
    name="openclaw-skills",
    description="Collection of OpenClaw skills",
    private=False
)

# Skill veröffentlichen
publish_skill(
    skill_name="image-generation",
    repo_name="openclaw-skills",
    description="Free image generation"
)

# Alle Skills
publish_all_skills(repo_name="openclaw-skills")
```

## Repository-Struktur

Nach Veröffentlichung:

```
openclaw-skills/
├── README.md              # Haupt-README
├── LICENSE
├── .gitignore
├── image-generation/
│   ├── README.md          # Skill-Dokumentation
│   ├── SKILL.md           # Original
│   └── scripts/
│       └── generate_image.py
├── piper-tts/
│   ├── README.md
│   ├── SKILL.md
│   └── scripts/
│       └── piper_tts.py
└── ...
```

## Automatisierung

### Cron-Job für Auto-Sync
```bash
# Alle 24h automatisch pushen
0 2 * * * cd ~/.openclaw/workspace && \
    python3 skills/github-manager/scripts/github_publish.py --all
```

### Bei Git-Commits
```bash
# In .git/hooks/post-commit:
#!/bin/bash
python3 skills/github-manager/scripts/github_publish.py --all
```

## Fehlerbehebung

| Fehler | Lösung |
|--------|--------|
| "401 Bad credentials" | Token prüfen/erneuern |
| "404 Repository not found" | Repo-Name prüfen |
| "403 API rate limit" | Weniger Requests oder Token mit höherem Limit |
| "Validation failed" | Repo-Name enthält ungültige Zeichen |

## GitHub Actions (optional)

Für automatische Tests:

```yaml
# .github/workflows/test.yml
name: Test Skills
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Python scripts
        run: |
          python3 -m py_compile */scripts/*.py
```

---

*Skills veröffentlichen leicht gemacht – für Eure Lordschaft!* 🐙🎩
