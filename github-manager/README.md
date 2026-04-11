# GitHub Manager Skill

Skills zu GitHub veröffentlichen und Repository-Verwaltung.

## Features

- 🐙 **Repository erstellen** - Neue Repos für Skills
- 🔄 **Auto-Sync** - Skills zu GitHub pushen
- 📁 **Skill-Export** - Ordnerstruktur vorbereiten
- 🏷️ **Versionierung** - Tags und Releases
- 📖 **README-Generierung** - Automatische Dokumentation

## Schnellstart

```bash
# Einzelnen Skill veröffentlichen
python3 scripts/github_publish.py --skill image-generation --repo openclaw-skills

# Alle Skills synchronisieren
python3 scripts/github_publish.py --all --repo openclaw-skills

# Neues Repository erstellen
python3 scripts/github_publish.py --create-repo openclaw-skills --private false
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
# GitHub API
GITHUB_TOKEN=ghp_dein_personal_access_token
GITHUB_USERNAME=dein_username
GITHUB_EMAIL=deine_email@beispiel.de
```

**Token erstellen:** https://github.com/settings/tokens

**Berechtigungen:**
- ✅ `repo` - Repository-Zugriff
- ✅ `workflow` - GitHub Actions
- ✅ `write:packages` - Packages schreiben

## Parameter

| Parameter | Beschreibung |
|-----------|--------------|
| `--skill` | Skill-Name zu veröffentlichen |
| `--repo` | Ziel-Repository |
| `--all` | Alle Skills veröffentlichen |
| `--create-repo` | Neues Repository erstellen |
| `--description` | Repository-Beschreibung |
| `--private` | Privates Repository (true/false) |

## Python API

```python
from scripts.github_publish import publish_skill, create_repo

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
```

---

*Teil der OpenClaw Skills Collection* 🎩
