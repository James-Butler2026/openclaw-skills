# Mega Filehoster Skill

MEGA.nz Cloud Storage Verwaltung – Dateien hochladen, verwalten und teilen.

## Features

- ☁️ Dateien hochladen/herunterladen
- 📁 Verzeichnisse auflisten
- 🔗 Share-Links generieren
- 💾 Speicherplatz prüfen

## Installation

```bash
cd ~/.openclaw/workspace/skills/mega-filehoster/

# megatools muss installiert sein
# sudo apt install megatools
```

## Verwendung

```bash
# Datei hochladen
python3 scripts/mega_manager.py upload /pfad/zur/datei.txt

# Verzeichnis auflisten
python3 scripts/mega_manager.py list

# Share-Link erstellen
python3 scripts/mega_manager.py share /datei.txt

# Speicherplatz anzeigen
python3 scripts/mega_manager.py quota
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
MEGA_EMAIL=dein-email@example.com
MEGA_PASSWORD=dein_passwort
```

## Sicherheit

- **WICHTIG:** Passwort niemals committen!
- **WICHTIG:** `.env` in `.gitignore` belassen!
- Bei Verdacht auf Leak: MEGA-Passwort ändern

---
*MEGA.nz Integration für OpenClaw* ☁️
