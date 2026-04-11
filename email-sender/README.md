# Email Sender Skill

Einfaches Versenden von E-Mails via SMTP.

## Features

- 📧 Unterstützt: Web.de, Gmail, GMX, eigene SMTP-Server
- 🔐 App-Passwörter für Gmail
- 🐍 Einfache Python API
- ✅ Keine externen Abhängigkeiten (Python Standardlib)

## Schnellstart

```bash
# Einfache E-Mail
python3 scripts/send_email.py \
    --to empfaenger@example.com \
    --subject "Hallo" \
    --body "Das ist ein Test"

# Mit spezifischem Provider
python3 scripts/send_email.py \
    --to freund@gmail.com \
    --subject "Treffen morgen" \
    --body "Hallo, wir treffen uns um 15 Uhr." \
    --provider webde

# Inhalt aus Datei
python3 scripts/send_email.py \
    --to chef@firma.de \
    --subject "Bericht" \
    --body-file bericht.txt
```

## Konfiguration

Füge zu deiner `.env` hinzu:

```bash
# Web.de Beispiel
WEBDE_EMAIL=deine_email@web.de
WEBDE_PASSWORD=dein_passwort
WEBDE_SMTP_SERVER=smtp.web.de
WEBDE_SMTP_PORT=587

# Gmail Beispiel (App-Passwort nötig!)
GMAIL_EMAIL=deine_email@gmail.com
GMAIL_PASSWORD=dein_app_passwort
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
```

**Wichtig für Gmail:**
- Normales Passwort funktioniert NICHT
- 2FA aktivieren → App-Passwort erstellen → Dieses verwenden

## Python API

```python
from scripts.send_email import send_email

send_email(
    to="empfaenger@example.com",
    subject="Hallo",
    body="Das ist ein Test",
    provider="webde"
)
```

## Fehlerbehebung

| Fehler | Lösung |
|--------|--------|
| "Authentication failed" | Passwort prüfen, für Gmail App-Passwort verwenden |
| "Connection refused" | Firewall/SMTP-Port prüfen (meist 587 oder 465) |
| "Recipient rejected" | Empfänger-Adresse auf Tippfehler prüfen |
| "SSL error" | Port auf 465 (SSL) oder 587 (STARTTLS) ändern |

---

*Teil der OpenClaw Skills Collection* 🎩
