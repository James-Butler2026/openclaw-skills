#!/usr/bin/env python3
"""
Email Sender v2.0 - Verbesserte Version mit MiniMax-Optimierungen
- E-Mail Validierung
- Retry-Logik mit Exponential Backoff
- Timeout-Handling
- Richtiges Logging
- HTML-E-Mail Unterstützung
- CC/BCC Felder
"""

import argparse
import logging
import os
import re
import smtplib
import ssl
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Optional, Union


# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_sender')


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


def validate_email(email: str) -> bool:
    """
    Validiert eine E-Mail-Adresse mit Regex
    
    Args:
        email: Zu validierende E-Mail-Adresse
    
    Returns:
        True wenn gültig, False sonst
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_emails(emails: List[str]) -> tuple[List[str], List[str]]:
    """
    Validiert eine Liste von E-Mail-Adressen
    
    Args:
        emails: Liste von E-Mail-Adressen
    
    Returns:
        Tuple: (gültige_emails, ungültige_emails)
    """
    valid = []
    invalid = []
    
    for email in emails:
        email = email.strip()
        if email:
            if validate_email(email):
                valid.append(email)
            else:
                invalid.append(email)
    
    return valid, invalid


def get_provider_config(provider: str) -> dict:
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
    
    # E-Mail validieren
    if not validate_email(email):
        raise ValueError(f"Ungültige Absender-E-Mail: {email}")
    
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


def send_email_with_retry(
    to: Union[str, List[str]],
    subject: str,
    body: str,
    provider: str = 'webde',
    from_email: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    html: bool = False,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> bool:
    """
    Sendet eine E-Mail mit Retry-Logik und Timeout
    
    Args:
        to: Empfänger E-Mail oder Liste
        subject: Betreff
        body: Nachrichtentext
        provider: Anbieter (webde, gmail, gmx, custom)
        from_email: Optional: Absender überschreiben
        cc: CC Empfänger (optional)
        bcc: BCC Empfänger (optional)
        html: True für HTML-E-Mail, False für Plain Text
        timeout: Timeout in Sekunden für SMTP-Verbindung
        max_retries: Maximale Anzahl Versuche
        retry_delay: Basis-Verzögerung zwischen Versuchen (wird exponentiell erhöht)
    
    Returns:
        True bei Erfolg
    
    Raises:
        Exception bei wiederholtem Fehlschlagen
    """
    # .env laden
    load_env_file()
    
    # Provider-Konfiguration holen
    config = get_provider_config(provider)
    
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    email = from_email or config['email']
    password = config['password']
    
    # Empfänger normalisieren
    to_list = [to] if isinstance(to, str) else to
    cc_list = [cc] if isinstance(cc, str) else (cc or [])
    bcc_list = [bcc] if isinstance(bcc, str) else (bcc or [])
    
    # Alle E-Mails validieren
    all_recipients = to_list + cc_list + bcc_list
    valid_emails, invalid_emails = validate_emails(all_recipients)
    
    if invalid_emails:
        raise ValueError(f"Ungültige E-Mail-Adressen: {', '.join(invalid_emails)}")
    
    if not valid_emails:
        raise ValueError("Keine gültigen Empfänger angegeben!")
    
    logger.info(f"Sende E-Mail...")
    logger.info(f"   Von: {email}")
    logger.info(f"   An: {', '.join(to_list)}")
    if cc_list:
        logger.info(f"   CC: {', '.join(cc_list)}")
    if bcc_list:
        logger.info(f"   BCC: {len(bcc_list)} Empfänger")
    logger.info(f"   Betreff: {subject}")
    logger.info(f"   Server: {smtp_server}:{smtp_port}")
    logger.info(f"   HTML: {html}")
    
    # E-Mail erstellen
    msg = MIMEMultipart('alternative')
    msg['From'] = email
    msg['To'] = ', '.join(to_list)
    
    if cc_list:
        msg['Cc'] = ', '.join(cc_list)
    
    msg['Subject'] = subject
    
    # Body hinzufügen (Plain Text und/oder HTML)
    if html:
        # HTML-Version
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        # Plain Text als Fallback
        plain_text = re.sub(r'<[^>]+>', '', body)  # HTML-Tags entfernen
        msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Alle Empfänger für send_message
    all_recipients_for_send = to_list + cc_list + bcc_list
    
    # Retry-Logik mit Exponential Backoff
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f"Verbindungsversuch {attempt}/{max_retries}...")
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
                server.starttls(context=context)
                server.login(email, password)
                server.send_message(msg)
            
            logger.info(f"✅ E-Mail erfolgreich gesendet!")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error("Authentifizierung fehlgeschlagen!")
            raise Exception(
                "Authentifizierung fehlgeschlagen!\n"
                "- Passwort prüfen\n"
                "- Für Gmail: App-Passwort verwenden (nicht normales Passwort)\n"
                "- 2FA prüfen"
            ) from e
            
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError) as e:
            # Diese Fehler sind nicht retry-bar
            logger.error(f"Nicht-retry-barer Fehler: {e}")
            raise
            
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, 
                TimeoutError, OSError) as e:
            # Diese Fehler sind retry-bar
            last_error = e
            logger.warning(f"Versuch {attempt} fehlgeschlagen: {e}")
            
            if attempt < max_retries:
                delay = retry_delay * (2 ** (attempt - 1))  # Exponential Backoff
                logger.info(f"Warte {delay:.1f}s vor nächstem Versuch...")
                time.sleep(delay)
            else:
                logger.error(f"Alle {max_retries} Versuche fehlgeschlagen")
                raise Exception(
                    f"SMTP-Verbindung nach {max_retries} Versuchen fehlgeschlagen: {last_error}"
                ) from last_error
        
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            raise
    
    return False


# Abwärtskompatibilität: Alte send_email Funktion
def send_email(
    to: str,
    subject: str,
    body: str,
    provider: str = 'webde',
    from_email: Optional[str] = None
) -> bool:
    """
    Legacy-Funktion für Abwärtskompatibilität
    Ruft send_email_with_retry mit Standard-Parametern auf
    """
    return send_email_with_retry(
        to=to,
        subject=subject,
        body=body,
        provider=provider,
        from_email=from_email,
        html=False,
        timeout=30,
        max_retries=1  # Legacy: Keine Retries
    )


def main():
    parser = argparse.ArgumentParser(
        description='Sendet E-Mails via SMTP (v2.0 mit MiniMax-Optimierungen)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --to freund@example.com --subject "Hallo" --body "Test"
  %(prog)s -t chef@firma.de -s "Bericht" -b "Siehe Anhang" -p webde
  %(prog)s -t admin@server.de -s "ALARM" -f alert.txt --html
  %(prog)s -t user@example.com -s "Newsletter" --cc "cc@example.com" -b "<h1>HTML</h1>"
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
    parser.add_argument('--cc', help='CC Empfänger (kommagetrennt)')
    parser.add_argument('--bcc', help='BCC Empfänger (kommagetrennt)')
    parser.add_argument('--html', action='store_true', 
                       help='E-Mail als HTML senden')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Timeout in Sekunden (Default: 30)')
    parser.add_argument('--retries', type=int, default=3,
                       help='Maximale Retry-Versuche (Default: 3)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Detaillierte Ausgabe')
    
    args = parser.parse_args()
    
    # Logging-Level anpassen
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Body aus Datei oder Parameter
    if args.body_file:
        try:
            with open(args.body_file, 'r', encoding='utf-8') as f:
                body = f.read()
        except Exception as e:
            logger.error(f"Fehler beim Lesen der Datei: {e}")
            sys.exit(1)
    elif args.body:
        body = args.body
    else:
        logger.error("Fehler: --body oder --body-file erforderlich!")
        sys.exit(1)
    
    # CC/BCC parsen
    cc_list = [e.strip() for e in args.cc.split(',')] if args.cc else None
    bcc_list = [e.strip() for e in args.bcc.split(',')] if args.bcc else None
    
    # E-Mail senden
    try:
        send_email_with_retry(
            to=args.to,
            subject=args.subject,
            body=body,
            provider=args.provider,
            from_email=args.from_email,
            cc=cc_list,
            bcc=bcc_list,
            html=args.html,
            timeout=args.timeout,
            max_retries=args.retries
        )
    except Exception as e:
        logger.error(f"{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
