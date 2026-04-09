# WordPress Manager für OpenClaw

## Schnellstart

### 1. WordPress einrichten

**Application Password generieren:**
1. WordPress Admin → Benutzer → Profil
2. "Application Passwords" ausklappen
3. Name eingeben: "OpenClaw"
4. Passwort kopieren (sieht aus wie: `WS25 cuTO Tlga gduz 5DuJ 8UjM`)

### 2. OpenClaw konfigurieren

In `.env` eintragen:
```bash
WORDPRESS_URL=https://dein-blog.de
WORDPRESS_USERNAME=dein_wp_benutzername
WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx
```

### 3. Kopieren

```bash
cp -r wordpress-manager ~/.openclaw/workspace/skills/
```

### 4. Test

```bash
python3 ~/.openclaw/workspace/skills/wordpress-manager/wordpress_manager.py --list
```

## Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `--list` | Alle Beiträge anzeigen |
| `--drafts` | Entwürfe anzeigen |
| `--create "Titel" "Inhalt"` | Neuen Beitrag erstellen |
| `--update ID --title "Neuer"` | Beitrag aktualisieren |
| `--delete ID` | In Papierkorb verschieben |
| `--delete ID --force` | Dauerhaft löschen |
| `--list-categories` | Kategorien anzeigen |

## Beispiel

```bash
# Neuen Beitrag erstellen
python3 wordpress_manager.py --create "Mein Titel" "<p>HTML Inhalt</p>" --status publish

# Als Entwurf speichern
python3 wordpress_manager.py --create "Titel" "Inhalt" --status draft

# Beitrag bearbeiten
python3 wordpress_manager.py --update 42 --title "Neuer Titel"
```

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "401 Unauthorized" | Benutzerrolle auf "Author"+ setzen |
| "403 Cloudflare" | WAF-Regel für Server-IP erstellen |
| "No module named" | Keine – Script nutzt nur Python-Standardlib |

## Features

- 🚀 **Cloudflare-kompatibel** – Realistische Browser-Header
- 🔒 **Sicher** – Application Passwords (kein Passwort im Klartext)
- 📦 **Stand-alone** – Keine externen Abhängigkeiten
- 📝 **Vollständig** – CRUD + Kategorien + Tags

---
**Autor:** James 🎩 | **Version:** 1.0.0
