---
name: wordpress-manager
description: Verwaltet WordPress-Beiträge via REST API – Beiträge erstellen, bearbeiten, löschen und verwalten. Cloudflare-kompatibel.
---

# WordPress Manager Skill

Verwaltet WordPress-Beiträge via REST API – Beiträge erstellen, bearbeiten, löschen und verwalten.

## Beschreibung

Dieser Skill ermöglicht die Verwaltung von WordPress-Beiträgen über die REST API. Unterstützt Cloudflare-geschützte Websites durch realistische Browser-Header.

## Installation

### 1. Voraussetzungen

- Python 3.8+
- WordPress mit REST API aktiviert
- Application Password in WordPress generiert

### 2. WordPress einrichten

1. **WordPress Application Password generieren:**
   - WP-Admin → Benutzer → Profil
   - "Application Passwords" → Name eingeben (z.B. "OpenClaw")
   - Passwort kopieren (Format: `xxxx xxxx xxxx xxxx`)

2. **Benutzerberechtigungen prüfen:**
   - Der Benutzer benötigt mindestens "Author"-Rolle
   - Empfohlen: "Editor" oder "Administrator"

### 3. Skill installieren

```bash
# Skill-Verzeichnis erstellen
mkdir -p ~/.openclaw/workspace/skills/wordpress-manager

# Dateien kopieren
cp wordpress_manager.py ~/.openclaw/workspace/skills/wordpress-manager/
cp SKILL.md ~/.openclaw/workspace/skills/wordpress-manager/
```

### 4. Umgebungsvariablen setzen

In `.env` im OpenClaw-Workspace:

```bash
# WordPress REST API
WORDPRESS_URL=https://dein-blog.de
WORDPRESS_USERNAME=dein_wp_benutzername
WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx
```

### 5. Test

```bash
python3 ~/.openclaw/workspace/skills/wordpress-manager/wordpress_manager.py --list
```

## Verwendung

### Als Python-Script

```bash
# Alle Beiträge anzeigen
python3 wordpress_manager.py --list

# Neuen Beitrag erstellen
python3 wordpress_manager.py --create "Titel" "HTML-Inhalt"

# Als Entwurf speichern
python3 wordpress_manager.py --create "Titel" "Inhalt" --status draft

# Beitrag bearbeiten
python3 wordpress_manager.py --update 42 --title "Neuer Titel"

# Beitrag löschen (Papierkorb)
python3 wordpress_manager.py --delete 42

# Dauerhaft löschen
python3 wordpress_manager.py --delete 42 --force

# Kategorien anzeigen
python3 wordpress_manager.py --list-categories
```

### Über OpenClaw

```bash
# In OpenClaw integrieren
openclaw wordpress list
openclaw wordpress create "Titel" "Inhalt"
openclaw wordpress update 42 --title "Neuer Titel"
```

## Features

- ✅ **Cloudflare-kompatibel** – Umgeht Bot-Schutz mit realistischen Headern
- ✅ **Keine externen Abhängigkeiten** – Nur Python-Standardbibliothek
- ✅ **Sichere Authentifizierung** – WordPress Application Passwords
- ✅ **CRUD-Operationen** – Create, Read, Update, Delete Beiträge
- ✅ **Kategorien & Tags** – Verwaltung von Taxonomien

## Fehlerbehebung

### "Access denied" / Cloudflare 1010
→ User-Agent ist bereits im Script integriert. Falls weiterhin blockiert:
→ Cloudflare → Security → WAF → Server-IP whitelisten

### "401 Unauthorized"
→ Application Password überprüfen
→ Benutzerrolle auf "Author" oder höher setzen

### "403 Forbidden"
→ REST API ist möglicherweise deaktiviert
→ Plugin "WordPress REST API Authentication" installieren

## Autor

OpenClaw Assistent 🎩
Version 1.0.0
