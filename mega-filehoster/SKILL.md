---
name: mega-filehoster
description: |
  MEGA.nz Filehoster Skill - Dateien in die MEGA Cloud hochladen, verwalten und teilen.
  Nutze diesen Skill wenn: (1) Dateien zu MEGA hochladen, (2) Dateien von MEGA herunterladen,
  (3) Verzeichnisse auflisten, (4) Share-Links generieren, (5) Speicherplatz prüfen.
---

# MEGA.nz Filehoster Skill

Ein vollständiger Skill zur Verwaltung von MEGA.nz Cloud Storage.

## ✨ Features

- 📤 **Dateien hochladen** - Lokale Dateien zu MEGA
- 📥 **Dateien herunterladen** - MEGA → Lokal
- 📁 **Verzeichnisse anzeigen** - Übersicht deiner Cloud
- 🔗 **Share-Links** - Dateien teilen
- 💾 **Speicherplatz** - Verfügbaren Platz prüfen

## 🚀 Schnellstart

### Installation

```bash
# MEGAtools installieren (falls nicht vorhanden)
apt-get install megatools  # Debian/Ubuntu
# oder: brew install megatools  # macOS
```

### Konfiguration (.env)

```bash
# Zu deiner .env hinzufügen:
MEGA_EMAIL=dein_mega_email@beispiel.de
MEGA_PASSWORD=dein_mega_passwort
```

### Nutzung

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

## 📁 Dateistruktur

```
mega-filehoster/
├── SKILL.md                 # Diese Datei
├── README.md                # Projektdokumentation
├── scripts/
│   └── mega_manager.py      # Hauptskript
└── references/
    └── megatools-docs.md    # Megatools Referenz
```

## 🔧 Technische Details

- **Backend:** megatools (mega-put, mega-get, mega-ls, mega-df)
- **Authentifizierung:** Via .env (MEGA_EMAIL, MEGA_PASSWORD)
- **Sicherheit:** Credentials nie committen!

## 📜 Lizenz

MIT - Frei nutzbar und modifizierbar.
