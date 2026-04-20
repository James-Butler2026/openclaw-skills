# WordPress Manager Skill

WordPress Beiträge via REST API verwalten – Cloudflare-kompatibel.

## Features

- 📝 REST API Integration
- 🛡️ Cloudflare-kompatibel
- 🔄 CRUD-Operationen
- 🏷️ Kategorien & Tags

## Installation

```bash
cd ~/.openclaw/workspace/skills/wordpress-manager/
```

## Verwendung

```bash
# Beiträge auflisten
python3 scripts/wordpress_manager.py --list

# Beitrag erstellen
python3 scripts/wordpress_manager.py \
    --create "Titel" "HTML-Inhalt"

# Als Entwurf speichern
python3 scripts/wordpress_manager.py \
    --create "Titel" "Inhalt" \
    --status draft

# Beitrag aktualisieren
python3 scripts/wordpress_manager.py \
    --update 42 --title "Neuer Titel"
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
WORDPRESS_URL=https://dein-blog.de
WORDPRESS_USERNAME=dein_benutzer
WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx
```

**API-Key erstellen:** WordPress Admin → Benutzer → Application Passwords

## Sicherheit

- **WICHTIG:** API-Key niemals committen!
- **WICHTIG:** Application Passwords verwenden, nicht normales Passwort!
- Bei Verdacht auf Leak: Passwort sofort ändern

---
*WordPress-Verwaltung für OpenClaw* 📝
