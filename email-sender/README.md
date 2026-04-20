# Email Sender Skill

E-Mails via SMTP senden – unterstützt Web.de, Gmail, GMX und eigene Server.

## Features

- 📧 Unterstützt Web.de, Gmail, GMX, eigene SMTP-Server
- 🔐 App-Passwörter für Gmail
- 🐍 Einfache Python API
- 🚫 Keine externen Abhängigkeiten

## Installation

```bash
cd ~/.openclaw/workspace/skills/email-sender/
```

## Verwendung

```bash
# E-Mail senden
python3 scripts/send_email.py \
    --to empfaenger@example.com \
    --subject "Hallo" \
    --body "Testnachricht"

# Mit Web.de
python3 scripts/send_email.py \
    --to freund@gmail.com \
    --subject "Treffen" \
    --body "Wir treffen uns um 15 Uhr" \
    --provider webde
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
# Web.de Beispiel
WEBDE_EMAIL=deine-email@web.de
WEBDE_PASSWORD=dein_passwort
WEBDE_SMTP_SERVER=smtp.web.de
WEBDE_SMTP_PORT=587

# Gmail Beispiel (App-Passwort nötig!)
GMAIL_EMAIL=dein.name@gmail.com
GMAIL_PASSWORD=dein_app_passwort
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
```

## Sicherheit

- **WICHTIG:** `.env` Datei niemals committen!
- **WICHTIG:** Für Gmail immer App-Passwörter verwenden!
- Keine Passwörter in Chat-Nachrichten schreiben
- Bei verdächtigen Aktivitäten: Passwort ändern

---
*E-Mail-Versenden für OpenClaw* 📧
