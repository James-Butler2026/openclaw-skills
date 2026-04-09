#!/usr/bin/env python3
"""
Email Sender - Sendet E-Mails via SMTP
Nutzt Zugangsdaten aus .env Datei
"""

import argparse
import os
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


# Standard-Konfigurationen für Provider
DEFAULT_PROVIDERS = {
    'webde': {
        'smtp_server': 'smtp.web.de',
        'smtp_port': 587,
        'email_env': 'WEBDE_EMAIL',
        'password_env': 'WEBDE_PASSWORD',
    },
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email_env': 'GMAIL_EMAIL',
        'password_env': 'GMAIL_PASSWORD',
    },
    'gmx': {
        'smtp_server': 'mail.gmx.net',
        'smtp_port': 587,
        'email_env': 'GMX_EMAIL',
        'password_env': 'GMX_PASSWORD',
    },
    'custom': {
        'smtp_server_env': 'CUSTOM_SMTP_SERVER',
        'smtp_port_env': 'CUSTOM_SMTP_PORT',
        'email_env': 'CUSTOM_EMAIL',
        'password_env': 'CUSTOM_PASSWORD',
    }
}


def load_env_file():
    """Lädt .env Datei falls vorhanden"""
    env_path = Path.home() / '.openclaw' / 'workspace' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value


def get_provider_config(provider):
    """Holt Provider-Konfiguration aus .env"""
    provider = provider.lower()
    
    if provider not in DEFAULT_PROVIDERS:
        raise ValueError(f"Unbekannter Provider: {provider}. "
                        f"Verfügbar: {', '.join(DEFAULT_PROVIDERS.keys())}")
    
    config = DEFAULT_PROVIDERS[provider].copy()
    
    # E-Mail und Passwort aus Umgebungsvariablen laden
    email = os.getenv(config['email_env'])
    password = os.getenv(config['password_env'])
    
    if not email or not password:
        raise ValueError(
            f"{config['email_env']} oder {config['password_env']} nicht in .env gefunden!\n"
            f"Bitte in ~/.openclaw/workspace/.env eintragen."
        )
    
    config['email'] = email
    config['password'] = password
    
    # Für custom Provider: Server und Port auch aus .env laden
    if provider == 'custom':
        smtp_server = os.getenv(config['smtp_server_env'])
        smtp_port = os.getenv(config['smtp_port_env'])
        if not smtp_server or not smtp_port:
            raise ValueError(
                f"{config['smtp_server_env']} oder {config['smtp_port_env']} nicht gefunden!"
            )
        config['smtp_server'] = smtp_server
        config['smtp_port'] = int(smtp_port)
    
    return config


def send_email(to, subject, body, provider='webde', from_email=None):
    """
    Sendet eine E-Mail
    
    Args:
        to: Empfänger E-Mail
        subject: Betreff
        body: Nachrichtentext
        provider: Anbieter (webde, gmail, gmx, custom)
        from_email: Optional: Absender überschreiben
    
    Returns:
        True bei Erfolg
    """
    # .env laden
    load_env_file()
    
    # Provider-Konfiguration holen
    config = get_provider_config(provider)
    
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    email = from_email or config['email']
    password = config['password']
    
    print(f"📧 Sende E-Mail...")
    print(f"   Von: {email}")
    print(f"   An: {to}")
    print(f"   Betreff: {subject}")
    print(f"   Server: {smtp_server}:{smtp_port}")
    
    # E-Mail erstellen
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Verbindung herstellen
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email, password)
            server.send_message(msg)
        
        print(f"✅ E-Mail erfolgreich gesendet!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        raise Exception(
            "Authentifizierung fehlgeschlagen!\n"
            "- Passwort prüfen\n"
            "- Für Gmail: App-Passwort verwenden (nicht normales Passwort)\n"
            "- 2FA prüfen"
        )
    except smtplib.SMTPRecipientsRefused:
        raise Exception(f"Empfänger abgelehnt: {to}")
    except Exception as e:
        raise Exception(f"SMTP Fehler: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Sendet E-Mails via SMTP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --to freund@example.com --subject "Hallo" --body "Test"
  %(prog)s -t chef@firma.de -s "Bericht" -b "Siehe Anhang" -p webde
  %(prog)s -t admin@server.de -s "ALARM" -f alert.txt
        """
    )
    
    parser.add_argument('--to', '-t', required=True, help='Empfänger E-Mail')
    parser.add_argument('--subject', '-s', default='Nachricht', help='Betreff')
    parser.add_argument('--body', '-b', help='Nachrichtentext')
    parser.add_argument('--body-file', '-f', help='Text aus Datei laden')
    parser.add_argument('--provider', '-p', default='webde',
                       choices=['webde', 'gmail', 'gmx', 'custom'],
                       help='E-Mail Provider (Default: webde)')
    parser.add_argument('--from', dest='from_email', help='Absender überschreiben')
    
    args = parser.parse_args()
    
    # Body aus Datei oder Parameter
    if args.body_file:
        try:
            with open(args.body_file, 'r', encoding='utf-8') as f:
                body = f.read()
        except Exception as e:
            print(f"❌ Fehler beim Lesen der Datei: {e}")
            sys.exit(1)
    elif args.body:
        body = args.body
    else:
        print("❌ Fehler: --body oder --body-file erforderlich!")
        sys.exit(1)
    
    # E-Mail senden
    try:
        send_email(
            to=args.to,
            subject=args.subject,
            body=body,
            provider=args.provider,
            from_email=args.from_email
        )
    except Exception as e:
        print(f"\n❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
