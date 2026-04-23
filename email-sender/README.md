# Email Skill v3.0

Vollständiger E-Mail-Support: **Senden und Lesen** via SMTP + IMAP. Unterstützt Web.de, Gmail, GMX und eigene Server.

## Features

### Senden (SMTP)
- 📧 Web.de, Gmail, GMX, eigene SMTP-Server
- ✉️ **HTML-E-Mails** mit Plain-Text-Fallback
- 📎 **Anhänge** – Mehrere Dateianhänge pro E-Mail
- 📋 **CC/BCC** – Mehrere Empfänger
- 🔁 **Retry-Logik** – Exponential Backoff bei Verbindungsfehlern
- ⏱️ **Timeout-Handling** – Konfigurierbare Timeouts
- ✅ **E-Mail-Validierung** – Regex-Prüfung aller Adressen
- 🔐 App-Passwörter für Gmail

### Lesen (IMAP) — NEU in v3.0!
- 📬 Ungelesene E-Mails abrufen
- 🔍 Suche nach Betreff, Absender, Datum
- 📁 Ordner auflisten und wechseln
- 🧵 Thread-Verfolgung (Message-ID, References)
- 📝 Zusammenfassung generieren
- ✅ Als gelesen markieren
- 📎 Anhänge erkennen und Informationen anzeigen
- 📊 JSON-Ausgabe für programmatische Verarbeitung

- 🚫 Keine externen Abhängigkeiten – nur Python Standardlib!

## Schnellstart — Senden

```bash
# Einfache Text-E-Mail
python3 scripts/send_email_v2.py \
    --to empfaenger@example.com \
    --subject "Hallo" \
    --body "Das ist ein Test"

# HTML-E-Mail
python3 scripts/send_email_v2.py \
    --to freund@gmail.com \
    --subject "Schicke Nachricht" \
    --body "<h1>Hallo!</h1><p>Wie geht's?</p>" \
    --html

# Mit Anhängen
python3 scripts/send_email_v2.py \
    --to chef@firma.de \
    --subject "Bericht" \
    --body "Siehe Anhang" \
    --attach /tmp/report.pdf \
    --attach /tmp/chart.png

# Mit CC und BCC
python3 scripts/send_email_v2.py \
    --to chef@firma.de \
    --cc "assistent@firma.de, sekretaerin@firma.de" \
    --bcc "archiv@firma.de" \
    --subject "Bericht" \
    --body "Inhalt hier"
```

## Schnellstart — Lesen (IMAP)

```bash
# Ungelesene E-Mails
python3 scripts/imap_reader.py --unread

# Letzte 5 ungelesene
python3 scripts/imap_reader.py --unread --limit 5

# Alle E-Mails der letzten 3 Tage
python3 scripts/imap_reader.py --all --since 3

# Nach Absender suchen
python3 scripts/imap_reader.py --from "amazon"

# Nach Betreff suchen
python3 scripts/imap_reader.py --subject "Bestellung"

# Als JSON ausgeben
python3 scripts/imap_reader.py --unread --json

# Ordner auflisten
python3 scripts/imap_reader.py --folders

# Als gelesen markieren
python3 scripts/imap_reader.py --unread --mark-read
```

## Python API

### Senden

```python
from send_email_v2 import send_email_with_retry

send_email_with_retry(
    to="empfaenger@example.com",
    subject="Hallo",
    body="<h1>Status</h1><p>Alles OK!</p>",
    html=True,
    attachments=["/tmp/report.pdf"],
    provider="webde",
)
```

### Lesen

```python
from imap_reader import read_emails, summarize_emails, emails_to_json

# Ungelesene E-Mails holen
emails = read_emails(provider="webde", unread_only=True, limit=5)

# Zusammenfassung
print(summarize_emails(emails))

# JSON
print(emails_to_json(emails))
```

## Konfiguration

Erstelle `.env` im Workspace:
```bash
# Web.de
WEBDE_EMAIL=deine-email@web.de
WEBDE_PASSWORD=dein_passwort

# Gmail (App-Passwort nötig!)
GMAIL_EMAIL=dein.name@gmail.com
GMAIL_PASSWORD=dein_app_passwort

# GMX
GMX_EMAIL=deine-email@gmx.de
GMX_PASSWORD=dein_passwort
```

**Wichtig für Gmail:** 2FA aktivieren → App-Passwort erstellen → Dieses verwenden!

## Sicherheit

- ⚠️ `.env` Datei niemals committen!
- ⚠️ Für Gmail immer App-Passwörter verwenden!
- Keine Passwörter in Chat-Nachrichten schreiben
- Bei verdächtigen Aktivitäten: Passwort ändern

## Changelog

### v3.0 (23.04.2026)
- ✅ **IMAP-Reader** — E-Mails lesen, suchen, zusammenfassen
- ✅ **Attachments** — Mehrere Dateianhänge beim Senden
- ✅ **JSON-Ausgabe** — Programmatische Verarbeitung
- ✅ **Thread-Verfolgung** — Message-ID/References-basiert
- ✅ **Ordner-Verwaltung** — Liste und Wechsel

### v2.0 (21.04.2026)
- ✅ Retry-Logik mit Exponential Backoff
- ✅ HTML-E-Mail Unterstützung
- ✅ CC und BCC Felder
- ✅ E-Mail-Validierung

### v1.0
- Initiale Version

---
*E-Mail-Senden UND -Lesen – der vollständige Butler-Service!* 📧🎩