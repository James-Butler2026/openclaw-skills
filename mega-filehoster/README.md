# MEGA.nz Filehoster Skill

Vollständige MEGA.nz Cloud Storage Verwaltung.

## Features

- 📤 **Dateien hochladen** - Lokale Dateien zu MEGA
- 📥 **Dateien herunterladen** - MEGA → Lokal
- 📁 **Verzeichnisse anzeigen** - Übersicht deiner Cloud
- 🔗 **Share-Links** - Dateien teilen
- 💾 **Speicherplatz** - Verfügbaren Platz prüfen

## Schnellstart

```bash
# Datei hochladen
python3 scripts/mega_manager.py upload /pfad/zur/datei.txt

# Datei herunterladen
python3 scripts/mega_manager.py download /mega/pfad/datei.txt /lokal/ziel/

# Verzeichnis anzeigen
python3 scripts/mega_manager.py list /mega/pfad/

# Share-Link erstellen
python3 scripts/mega_manager.py share /mega/pfad/datei.txt

# Speicherplatz anzeigen
python3 scripts/mega_manager.py quota
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
# MEGA.nz Account
MEGA_EMAIL=dein_mega_email@beispiel.de
MEGA_PASSWORD=dein_mega_passwort
```

## Installation

```bash
# MEGAtools installieren (falls nicht vorhanden)
apt-get install megatools  # Debian/Ubuntu
# oder: brew install megatools  # macOS
```

## Technische Details

- **Backend:** megatools (mega-put, mega-get, mega-ls, mega-df)
- **Authentifizierung:** Via .env (MEGA_EMAIL, MEGA_PASSWORD)

---

*Teil der OpenClaw Skills Collection* 🎩
