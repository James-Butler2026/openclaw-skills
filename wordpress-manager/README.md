# WordPress Manager Skill

WordPress Beiträge via REST API verwalten.

## Features

- ✅ **Cloudflare-kompatibel** - Umgeht Bot-Schutz
- ✅ **Keine externen Abhängigkeiten** - Python Standardlib
- ✅ **Sichere Authentifizierung** - Application Passwords
- ✅ **CRUD-Operationen** - Create, Read, Update, Delete
- ✅ **Kategorien & Tags** - Taxonomie-Verwaltung

## Schnellstart

```bash
# Alle Beiträge anzeigen
python3 scripts/wordpress_manager.py --list

# Neuen Beitrag erstellen
python3 scripts/wordpress_manager.py --create "Titel" "HTML-Inhalt"

# Als Entwurf speichern
python3 scripts/wordpress_manager.py --create "Titel" "Inhalt" --status draft

# Beitrag bearbeiten
python3 scripts/wordpress_manager.py --update 42 --title "Neuer Titel"

# Beitrag löschen (Papierkorb)
python3 scripts/wordpress_manager.py --delete 42

# Dauerhaft löschen
python3 scripts/wordpress_manager.py --delete 42 --force

# Kategorien anzeigen
python3 scripts/wordpress_manager.py --list-categories
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
# WordPress REST API
WORDPRESS_URL=https://dein-blog.de
WORDPRESS_USERNAME=dein_wp_benutzername
WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx
```

**API Key erstellen:**
1. WP-Admin → Benutzer → Profil
2. "Application Passwords" → Name eingeben (z.B. "OpenClaw")
3. Passwort kopieren

**Hinweis:** Benutzer benötigt mindestens "Author"-Rolle.

## Kommentare verwalten

```bash
# Neue Kommentare anzeigen
python3 scripts/wordpress_manager.py --comments --status hold

# Kommentar freischalten
python3 scripts/wordpress_manager.py --approve-comment 123

# Auf Kommentar antworten
python3 scripts/wordpress_manager.py --reply-comment 123 --reply-text "Danke!"

# Kommentar löschen
python3 scripts/wordpress_manager.py --delete-comment 123
```

## Fehlerbehebung

| Fehler | Lösung |
|--------|--------|
| "401 Unauthorized" | Application Password überprüfen |
| "403 Forbidden" | Benutzerrolle auf "Author"+ setzen |
| Cloudflare Block | User-Agent ist integriert, ggf. WAF-Regel für Server-IP |

---

*Teil der OpenClaw Skills Collection* 🎩
