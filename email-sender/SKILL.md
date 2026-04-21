---
name: email-sender
description: Send emails via SMTP using configured accounts (Web.de, Gmail, etc.). Supports plain text and HTML emails with CC/BCC. Features retry-logic, timeout handling, and proper logging. Uses credentials from .env file. Perfect for quick notifications, alerts, and automated messages.
version: 2.0
---

# Email Sender Skill v2.0

Einfaches Versenden von E-Mails via SMTP mit MiniMax-Optimierungen. Nutzt konfigurierte Accounts aus der .env Datei.

## ✨ Neue Features in v2.0

- 🔁 **Retry-Logik** – Automatische Wiederholung bei Verbindungsfehlern
- ⏱️ **Timeout-Handling** – Konfigurierbare Timeouts
- 📝 **Richtiges Logging** – Professionelles Logging statt print()
- 🌐 **HTML-E-Mails** – HTML-Formatierung unterstützt
- 📋 **CC/BCC** – Mehrere Empfänger mit CC und BCC
- ✉️ **E-Mail-Validierung** – Automatische Prüfung aller Adressen
- 🔙 **Abwärtskompatibel** – Alte API weiterhin nutzbar

## Voraussetzungen

### 1. SMTP-Zugangsdaten in .env eintragen

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

**Wichtig für Gmail:**
- Normales Passwort funktioniert NICHT
- 2FA aktivieren → App-Passwort erstellen → Dieses verwenden

### 2. Python-Abhängigkeiten

Keine zusätzlichen Packages nötig – nutzt nur Python Standardlib!

## Schnellstart

### Einzelne E-Mail senden (v2.0)
```bash
# Einfachste Variante
python3 skills/email-sender/scripts/send_email_v2.py \
    --to empfaenger@example.com \
    --subject "Hallo" \
    --body "Das ist ein Test"

# Mit HTML
python3 skills/email-sender/scripts/send_email_v2.py \
    --to freund@gmail.com \
    --subject "Schicke Nachricht" \
    --body "<h1>Hallo!</h1><p>Wie geht's?</p>" \
    --html

# Mit CC und BCC
python3 skills/email-sender/scripts/send_email_v2.py \
    --to chef@firma.de \
    --cc "assistent@firma.de, sekretaerin@firma.de" \
    --bcc "archiv@firma.de" \
    --subject "Bericht" \
    --body "Siehe Anhang"
```

### Legacy-Version (v1.0)
```bash
# Alte Version für Abwärtskompatibilität
python3 skills/email-sender/scripts/send_email.py \
    --to empfaenger@example.com \
    --subject "Hallo" \
    --body "Test"
```

## Parameter (v2.0)

| Parameter | Kurzform | Beschreibung |
|-----------|----------|--------------|
| `--to` | `-t` | Empfänger E-Mail (erforderlich) |
| `--subject` | `-s` | Betreff (Default: "Nachricht") |
| `--body` | `-b` | Nachrichtentext |
| `--body-file` | `-f` | Text aus Datei laden |
| `--provider` | `-p` | Anbieter: webde, gmail, gmx, custom (Default: webde) |
| `--from` | | Absender überschreiben |
| `--cc` | | CC Empfänger (kommagetrennt) |
| `--bcc` | | BCC Empfänger (kommagetrennt) |
| `--html` | | E-Mail als HTML senden |
| `--timeout` | | Timeout in Sekunden (Default: 30) |
| `--retries` | | Maximale Retry-Versuche (Default: 3) |
| `--verbose` | `-v` | Detaillierte Ausgabe (DEBUG-Logging) |

## Python API

### Neue v2.0 API (empfohlen)
```python
from skills.email_sender.scripts.send_email_v2 import send_email_with_retry

# Einfacher Aufruf
send_email_with_retry(
    to="empfaenger@example.com",
    subject="Hallo",
    body="Das ist ein Test",
    provider="webde"
)

# Mit HTML und CC
send_email_with_retry(
    to="chef@firma.de",
    cc=["assistent@firma.de", "sekretaerin@firma.de"],
    subject="Wichtig!",
    body="<h1>Server Status</h1><p>Alles OK!</p>",
    html=True,
    provider="webde",
    timeout=30,
    max_retries=3
)
```

### Legacy API (v1.0)
```python
from skills.email_sender.scripts.send_email import send_email

# Abwärtskompatibel – funktioniert wie zuvor
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
| "Ungültige E-Mail-Adresse" | E-Mail-Format prüfen (name@domain.tld) |
| Timeout nach Retries | Netzwerkverbindung prüfen, `--retries` erhöhen |

## Sicherheitshinweise

⚠️ **Wichtig:**
- `.env` Datei niemals committen (ist bereits in .gitignore)
- Keine E-Mail-Adressen oder Passwörter in Code/Chat schreiben
- Für Gmail immer App-Passwörter verwenden (kein normales Passwort)
- Bei verdächtigen Aktivitäten: Passwort ändern

## Beispiele

### Cron-Job Benachrichtigung mit Retry
```bash
#!/bin/bash
# Im Cron-Job:

if ! ping -c 1 google.com; then
    python3 skills/email-sender/scripts/send_email_v2.py \
        --to admin@example.com \
        --subject "ALARM: Internet ausgefallen" \
        --body "$(date): Keine Internetverbindung!" \
        --retries 5
fi
```

### HTML-Newsletter
```bash
python3 skills/email-sender/scripts/send_email_v2.py \
    --to kunden@example.com \
    --cc "marketing@example.com" \
    --subject "Monatlicher Newsletter $(date +%B)" \
    --body-file newsletter.html \
    --html
```

### Täglicher Bericht mit Timeout
```bash
python3 skills/email-sender/scripts/send_email_v2.py \
    --to chef@firma.de \
    --bcc "archiv@firma.de" \
    --subject "Tagesbericht $(date +%Y-%m-%d)" \
    --body-file /var/log/daily-report.txt \
    --timeout 60 \
    --verbose
```

## Changelog

### v2.0 (21.04.2026)
- ✅ Retry-Logik mit Exponential Backoff
- ✅ Timeout-Handling für SMTP-Verbindungen
- ✅ Professionelles Logging (logging-Modul)
- ✅ HTML-E-Mail Unterstützung
- ✅ CC und BCC Felder
- ✅ E-Mail-Validierung mit Regex
- ✅ Abwärtskompatibilität zur v1.0

### v1.0
- Initiale Version mit Basis-Funktionalität

---

*E-Mail-Versenden leicht gemacht – für Eure Lordschaft!* 📧🎩
