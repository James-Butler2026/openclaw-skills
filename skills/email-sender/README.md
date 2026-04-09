# email-sender

---
name: email-sender
description: Send emails via SMTP using configured accounts (Web.de, Gmail, etc.). Supports plain text emails with custom subject and body. Uses credentials from .env file. Perfect for quick notifications, alerts, and automated messages.
---

# Email Sender Skill

Einfaches Versenden von E-Mails via SMTP. Nutzt konfigurierte Accounts aus der .env Datei.

## Voraussetzungen

### 1. SMTP-Zugangsdaten in .env eintragen

```bash
# Web.de Beispiel
WEBDE_EMAIL=j_butler@web.de
WEBDE_PASSWORD=dein_passwort
WEBDE_SMTP_SERVER=smtp.web.de
WEBDE_SMTP_PORT=587

# Gmail Beispiel (App-Passwort nötig!)
GMAIL_EMAIL=dein.name@gmail.com
GMAIL_PASSWORD=dein_app_passwort
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
```

**Wichtig für Gmail:**
- Normales Passwort funktioniert NICHT
- 2FA aktivieren → App-Passwort erstellen → Dieses verwenden

### 2. Python-Abhängigkeiten

Keine zusätzlichen Packages nötig – nutzt nur Python Standardlib!

## Schnellstart

### Einzelne E-Mail senden
```bash
# Einfachste Variante
python3 skills/email-sender/scripts/send_email.py \
    --to empfaenger@example.com \
    --subject "Hallo" \
    --body "Das ist ein Test"

# Mit Web.de (Default)
python3 skills/email-sender/scripts/send_email.py \
    --to freund@gmail.com \
    --subject "Treffen morgen" \
    --body "Hallo, wir treffen uns um 15 Uhr." \
    --provider webde
```

### E-Mail aus Datei
```bash
# Inhalt aus Textdatei
python3 skills/email-sender/scripts/send_email.py \
    --to chef@firma.de \
    --subject "Bericht" \
    --body-file bericht.txt
```

## Parameter

| Parameter | Kurzform | Beschreibung |
|-----------|----------|--------------|
| `--to` | `-t` | Empfänger E-Mail (erforderlich) |
| `--subject` | `-s` | Betreff (Default: "Nachricht") |
| `--body` | `-b` | Nachrichtentext |
| `--body-file` | `-f` | Text aus Datei laden |
| `--provider` | `-p` | Anbieter: webde, gmail, custom (Default: webde) |
| `--from` | `-f` | Absender (optional, überschreibt .env) |

## Konfiguration

### Neue Anbieter hinzufügen

In `~/.openclaw/workspace/.env` eintragen:

```bash
# Beispiel: GMX
GMX_EMAIL=dein.name@gmx.de
GMX_PASSWORD=dein_passwort
GMX_SMTP_SERVER=mail.gmx.net
GMX_SMTP_PORT=587

# Beispiel: Eigenes SMTP
CUSTOM_EMAIL=noreply@deine-domain.de
CUSTOM_PASSWORD=dein_passwort
CUSTOM_SMTP_SERVER=mail.deine-domain.de
CUSTOM_SMTP_PORT=587
```

## Python API

```python
from skills.email_sender.scripts.send_email import send_email

# Einfacher Aufruf
send_email(
    to="empfaenger@example.com",
    subject="Hallo",
    body="Das ist ein Test",
    provider="webde"
)

# Mit Exception-Handling
try:
    send_email(
        to="chef@firma.de",
        subject="Wichtig!",
        body="Der Server ist wieder online.",
        provider="webde"
    )
    print("✅ E-Mail gesendet")
except Exception as e:
    print(f"❌ Fehler: {e}")
```

## Fehlerbehebung

| Fehler | Lösung |
|--------|--------|
| "Authentication failed" | Passwort prüfen, für Gmail App-Passwort verwenden |
| "Connection refused" | Firewall/SMTP-Port prüfen (meist 587 oder 465) |
| "Recipient rejected" | Empfänger-Adresse auf Tippfehler prüfen |
| "SSL error" | Port auf 465 (SSL) oder 587 (STARTTLS) ändern |

## Sicherheitshinweise

⚠️ **Wichtig:**
- `.env` Datei niemals committen (ist bereits in .gitignore)
- Keine E-Mail-Passwörter in Chat-Nachrichten schreiben
- Für Gmail immer App-Passwörter verwenden (kein normales Passwort)
- Bei verdächtigen Aktivitäten: Passwort ändern

## Beispiele

### Cron-Job Benachrichtigung
```bash
#!/bin/bash
# Im Cron-Job:

if ! ping -c 1 google.com; then
    python3 skills/email-sender/scripts/send_email.py \
        --to admin@example.com \
        --subject "ALARM: Internet ausgefallen" \
        --body "$(date): Keine Internetverbindung!"
fi
```

### Täglicher Bericht
```bash
python3 skills/email-sender/scripts/send_email.py \
    --to chef@firma.de \
    --subject "Tagesbericht $(date +%Y-%m-%d)" \
    --body-file /var/log/daily-report.txt
```

---

*E-Mail-Versenden leicht gemacht – für Eure Lordschaft!* 📧🎩
