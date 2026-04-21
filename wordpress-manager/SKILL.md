---
name: wordpress-manager
description: Verwaltet WordPress-Beiträge via REST API – Beiträge erstellen, bearbeiten, löschen und verwalten. Cloudflare-kompatibel. Mit Retry-Logik, Pagination und Rate-Limit Handling.
version: 2.0.0
---

# WordPress Manager Skill v2.0

Verwaltet WordPress-Beiträge via REST API – Beiträge erstellen, bearbeiten, löschen und verwalten.

## ✨ Neue Features in v2.0

- 🔁 **Retry-Logik** – Automatische Wiederholung bei Verbindungsfehlern (Exponential Backoff)
- ⏱️ **Rate-Limit Handling** – Wartet bei 429 Too Many Requests automatisch
- 📊 **Pagination** – `--all` Flag für alle Posts über alle Seiten
- 📝 **Professionelles Logging** – logging-Modul statt print()
- 🔧 **Flexible Konfiguration** – Timeout und Retry über Umgebungsvariablen

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
cp wordpress_manager_v2.py ~/.openclaw/workspace/skills/wordpress-manager/
cp SKILL.md ~/.openclaw/workspace/skills/wordpress-manager/
```

### 4. Umgebungsvariablen setzen

In `.env` im OpenClaw-Workspace:

```bash
# WordPress REST API
WORDPRESS_URL=https://dein-blog.de
WORDPRESS_USERNAME=dein_wp_benutzername
WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx

# Optional: Timeout und Retry konfigurieren
WP_TIMEOUT=30
WP_MAX_RETRIES=3
```

### 5. Test

```bash
python3 ~/.openclaw/workspace/skills/wordpress-manager/wordpress_manager_v2.py --list
```

## Verwendung

### v2.0 (empfohlen)
```bash
# Beiträge auflisten
python3 wordpress_manager_v2.py --list

# Alle Beiträge (alle Seiten durchlaufen)
python3 wordpress_manager_v2.py --list --all

# Neuen Beitrag erstellen
python3 wordpress_manager_v2.py --create "Titel" "HTML-Inhalt"

# Beitrag bearbeiten
python3 wordpress_manager_v2.py --update 42 --title "Neuer Titel"

# Beitrag löschen (Papierkorb)
python3 wordpress_manager_v2.py --delete 42

# Kategorien anzeigen
python3 wordpress_manager_v2.py --list-categories

# Verbose Output (DEBUG-Logging)
python3 wordpress_manager_v2.py --list --verbose
```

### v1.0 (Legacy)
```bash
# Alte Version für Abwärtskompatibilität
python3 wordpress_manager.py --list
```

## Neue Parameter in v2.0

| Parameter | Kurzform | Beschreibung |
|-----------|----------|--------------|
| `--all` | | Alle Seiten durchlaufen (Pagination) |
| `--verbose` | `-v` | Detaillierte Ausgabe (DEBUG-Logging) |

## Umgebungsvariablen (v2.0)

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `WORDPRESS_URL` | (required) | WordPress URL |
| `WORDPRESS_USERNAME` | (required) | WordPress Benutzername |
| `WORDPRESS_API_KEY` | (required) | Application Password |
| `WP_TIMEOUT` | 30 | Timeout in Sekunden |
| `WP_MAX_RETRIES` | 3 | Maximale Retry-Versuche |

## Features

- ✅ **Cloudflare-kompatibel** – Umgeht Bot-Schutz mit realistischen Headern
- ✅ **Keine externen Abhängigkeiten** – Nur Python-Standardbibliothek
- ✅ **Sichere Authentifizierung** – WordPress Application Passwords
- ✅ **CRUD-Operationen** – Create, Read, Update, Delete Beiträge
- ✅ **Kategorien & Tags** – Verwaltung von Taxonomien
- ✅ **Retry-Logik** – Exponential Backoff bei Verbindungsfehlern
- ✅ **Rate-Limit Handling** – Wartet automatisch bei 429-Fehlern
- ✅ **Pagination** – Alle Posts durchlaufen mit `--all`

## Fehlerbehebung

| Fehler | Lösung |
|--------|--------|
| "Access denied" / Cloudflare 1010 | Server-IP in Cloudflare whitelisten |
| "401 Unauthorized" | Application Password prüfen |
| "403 Forbidden" | REST API ist deaktiviert |
| "429 Too Many Requests" | Automatisch – Script wartet und retryt |
| Timeout | `WP_TIMEOUT` erhöhen oder Netzwerk prüfen |

## Changelog

### v2.0 (21.04.2026)
- ✅ Retry-Logik mit Exponential Backoff
- ✅ Rate-Limit Handling (429 detection)
- ✅ Pagination mit `--all` Flag
- ✅ Professionelles Logging
- ✅ Konfigurierbarer Timeout via `WP_TIMEOUT`
- ✅ Max Retries via `WP_MAX_RETRIES`

### v1.0
- Initiale Version mit Basis-Funktionalität

## Autor

James – Ihr OpenClaw Butler 🎩
Version 2.0.0
