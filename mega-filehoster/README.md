# MEGA.nz Filehoster

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Einfacher Python-Wrapper für MEGA.nz Cloud Storage.

## 🚀 Installation

```bash
# megatools installieren
sudo apt-get install megatools  # Debian/Ubuntu
# oder: brew install megatools  # macOS
```

## ⚙️ Konfiguration

**WICHTIG:** Credentials NIEMALS committen!

1. Erstelle `.env` Datei (ist bereits in `.gitignore`):
```bash
MEGA_EMAIL=dein@email.com
MEGA_PASSWORD=dein_passwort
```

2. Oder exportiere als Umgebungsvariablen:
```bash
export MEGA_EMAIL=dein@email.com
export MEGA_PASSWORD=dein_passwort
```

## 📖 Nutzung

```bash
# Hochladen
python3 scripts/mega_manager.py upload /pfad/zur/datei.txt

# Herunterladen
python3 scripts/mega_manager.py download /mega/datei.txt /lokal/

# Auflisten
python3 scripts/mega_manager.py list /

# Speicherplatz
python3 scripts/mega_manager.py quota
```

## 🔒 Sicherheit

- **.env Datei** ist in `.gitignore` eingetragen
- **Credentials** werden nie im Code gespeichert
- **Nur lokal** in deiner Umgebung konfigurieren

## 📁 Projektstruktur

```
mega-filehoster/
├── SKILL.md
├── README.md
└── scripts/
    └── mega_manager.py
```

## 📝 Lizenz

MIT
