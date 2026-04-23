#!/usr/bin/env python3
"""
IMAP Email Reader - E-Mails lesen, suchen, zusammenfassen und beantworten
Nutzt Zugangsdaten aus .env Datei (wie email-sender v2)

Features:
- Ungelesene E-Mails abrufen
- Nach Betreff/Absender suchen
- E-Mail-Inhalt zusammenfassen
- Auf Threads antworten
- E-Mails als gelesen/markieren
- Ordner auflisten
"""

import argparse
import email
import email.policy
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import imaplib

# Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('imap_reader')

# Provider-Config (SMTP/IMAP Server sind oft verschieden)
IMAP_PROVIDERS = {
    'webde': {
        'imap_server': 'imap.web.de',
        'imap_port': 993,
        'email_env': 'WEBDE_EMAIL',
        'password_env': 'WEBDE_PASSWORD',
    },
    'gmail': {
        'imap_server': 'imap.gmail.com',
        'imap_port': 993,
        'email_env': 'GMAIL_EMAIL',
        'password_env': 'GMAIL_PASSWORD',
    },
    'gmx': {
        'imap_server': 'imap.gmx.net',
        'imap_port': 993,
        'email_env': 'GMX_EMAIL',
        'password_env': 'GMX_PASSWORD',
    },
    'custom': {
        'imap_server_env': 'CUSTOM_IMAP_SERVER',
        'imap_port_env': 'CUSTOM_IMAP_PORT',
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
                    os.environ.setdefault(key, value)


def decode_str(s) -> str:
    """Dekodiert Header-Strings (Betreff, Absender etc.)"""
    if s is None:
        return ''
    decoded_parts = decode_header(s)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or 'utf-8', errors='replace'))
        else:
            result.append(part)
    return ''.join(result)


def get_provider_config(provider: str) -> dict:
    """Holt IMAP Provider-Konfiguration aus .env"""
    provider = provider.lower()
    if provider not in IMAP_PROVIDERS:
        raise ValueError(f"Unbekannter Provider: {provider}. "
                        f"Verfügbar: {', '.join(IMAP_PROVIDERS.keys())}")
    
    config = IMAP_PROVIDERS[provider].copy()
    email_addr = os.getenv(config['email_env'])
    password = os.getenv(config['password_env'])
    
    if not email_addr or not password:
        raise ValueError(
            f"{config['email_env']} oder {config['password_env']} nicht in .env gefunden!"
        )
    
    config['email'] = email_addr
    config['password'] = password
    
    if provider == 'custom':
        imap_server = os.getenv(config.get('imap_server_env', ''))
        imap_port = os.getenv(config.get('imap_port_env', '993'))
        if not imap_server:
            raise ValueError("CUSTOM_IMAP_SERVER nicht in .env gefunden!")
        config['imap_server'] = imap_server
        config['imap_port'] = int(imap_port)
    
    return config


def connect_imap(provider: str = 'webde') -> imaplib.IMAP4_SSL:
    """Stellt IMAP-Verbindung her"""
    config = get_provider_config(provider)
    
    logger.info(f"Verbinde mit {config['imap_server']}:{config['imap_port']}...")
    
    imap = imaplib.IMAP4_SSL(config['imap_server'], config['imap_port'])
    imap.login(config['email'], config['password'])
    
    logger.info("✅ IMAP-Verbindung hergestellt")
    return imap


def get_body(msg, prefer_html: bool = False) -> str:
    """
    Extrahiert den Text-Inhalt einer E-Mail.
    
    Args:
        msg: Email-Message-Objekt
        prefer_html: Wenn True, wird HTML bevorzugt (sonst Plain Text)
    
    Returns:
        Text-Inhalt der E-Mail
    """
    body = ""
    html_body = ""
    plain_body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get('Content-Disposition', ''))
            
            # Attachments überspringen
            if 'attachment' in disposition:
                continue
            
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    text = payload.decode(charset, errors='replace')
                    
                    if content_type == 'text/plain':
                        plain_body = text
                    elif content_type == 'text/html':
                        html_body = text
            except Exception:
                continue
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='replace')
    
    if prefer_html and html_body:
        # HTML-Tags entfernen für lesbaren Text
        body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL)
        body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = re.sub(r'\s+', ' ', body).strip()
    elif plain_body:
        body = plain_body
    elif html_body:
        body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL)
        body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = re.sub(r'\s+', ' ', body).strip()
    
    # Auf max 5000 Zeichen kürzen
    if len(body) > 5000:
        body = body[:5000] + "\n\n[... gekürzt]"
    
    return body


def get_attachments(msg) -> List[Dict]:
    """Extrahiert Attachment-Infos aus einer E-Mail (ohne Download)"""
    attachments = []
    for part in msg.walk():
        disposition = str(part.get('Content-Disposition', ''))
        if 'attachment' in disposition:
            filename = decode_str(part.get_filename() or 'unnamed')
            content_type = part.get_content_type()
            size = len(part.get_payload(decode=True) or b'')
            attachments.append({
                'filename': filename,
                'content_type': content_type,
                'size_bytes': size,
                'size_readable': f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
            })
    return attachments


def parse_email(raw_email: bytes) -> Dict:
    """Parselt eine Raw-E-Mail in ein strukturiertes Dict"""
    msg = email.message_from_bytes(raw_email, policy=email.policy.default)
    
    subject = decode_str(msg.get('Subject', ''))
    from_addr = decode_str(msg.get('From', ''))
    to_addr = decode_str(msg.get('To', ''))
    date_str = msg.get('Date', '')
    message_id = msg.get('Message-ID', '')
    in_reply_to = msg.get('In-Reply-To', '')
    references = msg.get('References', '')
    
    body = get_body(msg)
    attachments = get_attachments(msg)
    
    return {
        'subject': subject,
        'from': from_addr,
        'to': to_addr,
        'date': date_str,
        'message_id': message_id,
        'in_reply_to': in_reply_to,
        'references': references,
        'body': body,
        'attachments': attachments,
        'body_length': len(body),
    }


def list_folders(provider: str = 'webde') -> List[str]:
    """Listet alle verfügbaren IMAP-Ordner auf"""
    imap = connect_imap(provider)
    try:
        status, folders = imap.list()
        if status != 'OK':
            logger.error("Ordner konnten nicht gelistet werden")
            return []
        
        result = []
        for folder_info in folders:
            if folder_info:
                # Parse "(\HasNoChildren) "/"INBOX" style output
                parts = folder_info.decode() if isinstance(folder_info, bytes) else folder_info
                # Extract folder name (last part, in quotes or not)
                match = re.search(r'"([^"]+)"$', parts)
                if match:
                    result.append(match.group(1))
                else:
                    result.append(parts.split()[-1].strip('"'))
        return sorted(result)
    finally:
        imap.logout()


def read_emails(
    provider: str = 'webde',
    folder: str = 'INBOX',
    unread_only: bool = True,
    limit: int = 10,
    search_subject: Optional[str] = None,
    search_from: Optional[str] = None,
    since_days: int = 7,
    mark_read: bool = False,
    prefer_html: bool = False,
) -> List[Dict]:
    """
    Liest E-Mails aus einem IMAP-Ordner.
    
    Args:
        provider: E-Mail Provider
        folder: IMAP-Ordner (Default: INBOX)
        unread_only: Nur ungelesene E-Mails
        limit: Maximale Anzahl E-Mails
        search_subject: Nach Betreff filtern (Substring)
        search_from: Nach Absender filtern
        since_days: Nur E-Mails der letzten N Tage
        mark_read: Gelesene E-Mails als gelesen markieren
        prefer_html: HTML-Inhalt bevorzugen
    
    Returns:
        Liste von E-Mail-Dicts
    """
    imap = connect_imap(provider)
    
    try:
        status, _ = imap.select(folder)
        if status != 'OK':
            raise ValueError(f"Ordner '{folder}' nicht gefunden!")
        
        # Suchkriterien aufbauen
        search_criteria = []
        
        if unread_only:
            search_criteria.append('UNSEEN')
        
        if search_subject:
            search_criteria.append(f'SUBJECT "{search_subject}"')
        
        if search_from:
            search_criteria.append(f'FROM "{search_from}"')
        
        if since_days > 0:
            since_date = (datetime.now() - timedelta(days=since_days)).strftime('%d-%b-%Y')
            search_criteria.append(f'SINCE {since_date}')
        
        # Suche ausführen
        if search_criteria:
            search_query = ' '.join(search_criteria)
        else:
            search_query = 'ALL'
        
        logger.info(f"Suche: {search_query}")
        status, message_ids = imap.search(None, search_query)
        
        if status != 'OK':
            logger.error("Suche fehlgeschlagen")
            return []
        
        id_list = message_ids[0].split()
        
        if not id_list:
            logger.info("Keine E-Mails gefunden")
            return []
        
        # Neueste zuerst, begrenzt auf limit
        id_list = id_list[-limit:][::-1]
        
        emails = []
        for mid in id_list:
            status, msg_data = imap.fetch(mid, '(RFC822)')
            if status != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            parsed = parse_email(raw_email)
            parsed['uid'] = mid.decode()
            
            if mark_read:
                imap.store(mid, '+FLAGS', '\\Seen')
            
            emails.append(parsed)
        
        logger.info(f"📬 {len(emails)} E-Mail(s) gefunden")
        return emails
        
    finally:
        imap.logout()


def get_email_by_uid(
    uid: str,
    provider: str = 'webde',
    folder: str = 'INBOX',
) -> Optional[Dict]:
    """
    Holt eine einzelne E-Mail per UID/Message-ID.
    """
    imap = connect_imap(provider)
    try:
        imap.select(folder)
        status, msg_data = imap.fetch(uid, '(RFC822)')
        if status != 'OK':
            return None
        raw_email = msg_data[0][1]
        return parse_email(raw_email)
    finally:
        imap.logout()


def summarize_emails(emails: List[Dict], max_body_length: int = 200) -> str:
    """
    Erstellt eine Zusammenfassung der E-Mails als formatierten Text.
    
    Args:
        emails: Liste von E-Mail-Dicts
        max_body_length: Maximal angezeigte Zeichen pro Body
    
    Returns:
        Formatierter Zusammenfassungstext
    """
    if not emails:
        return "📭 Keine E-Mails gefunden."
    
    lines = [f"📬 {len(emails)} E-Mail(s):\n"]
    
    for i, em in enumerate(emails, 1):
        lines.append(f"━━━ E-Mail {i} ━━━")
        lines.append(f"📤 Von: {em['from']}")
        lines.append(f"📥 An: {em['to']}")
        lines.append(f"📋 Betreff: {em['subject']}")
        lines.append(f"🕐 Datum: {em['date']}")
        
        if em['attachments']:
            att_str = ', '.join(f"{a['filename']} ({a['size_readable']})" for a in em['attachments'])
            lines.append(f"📎 Anhänge: {att_str}")
        
        # Body kürzen
        body = em.get('body', '')
        if len(body) > max_body_length:
            body = body[:max_body_length] + '...'
        if body.strip():
            lines.append(f"📝 Inhalt: {body}")
        
        lines.append('')
    
    return '\n'.join(lines)


def emails_to_json(emails: List[Dict]) -> str:
    """Konvertiert E-Mail-Liste zu JSON (für programmatische Verarbeitung)"""
    return json.dumps(emails, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description='IMAP Email Reader - E-Mails lesen, suchen und zusammenfassen',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --unread                          # Ungelesene E-Mails
  %(prog)s --unread --limit 5                 # Letzte 5 ungelesene
  %(prog)s --from "amazon"                    # Von Amazon
  %(prog)s --subject "Bestellung"             # Betreff enthält "Bestellung"
  %(prog)s --all --since 3                    # Alle E-Mails der letzten 3 Tage
  %(prog)s --unread --json                     # Als JSON ausgeben
  %(prog)s --folders                           # Ordner auflisten
  %(prog)s --mark-read --unread               # Ungelesene als gelesen markieren
        """
    )
    
    # Aktionen
    parser.add_argument('--folders', action='store_true',
                       help='IMAP-Ordner auflisten')
    
    # Filter
    parser.add_argument('--unread', action='store_true',
                       help='Nur ungelesene E-Mails')
    parser.add_argument('--all', action='store_true',
                       help='Alle E-Mails (auch gelesene)')
    parser.add_argument('--from', dest='search_from', help='Nach Absender filtern')
    parser.add_argument('--subject', help='Nach Betreff filtern')
    parser.add_argument('--since', type=int, default=7,
                       help='Letzte N Tage (Default: 7)')
    parser.add_argument('--folder', default='INBOX',
                       help='IMAP-Ordner (Default: INBOX)')
    parser.add_argument('--limit', type=int, default=10,
                       help='Maximale Anzahl E-Mails (Default: 10)')
    parser.add_argument('--mark-read', action='store_true',
                       help='Gelesene E-Mails als gelesen markieren')
    
    # Ausgabe
    parser.add_argument('--json', action='store_true',
                       help='Als JSON ausgeben')
    parser.add_argument('--full', action='store_true',
                       help='Vollständigen Body anzeigen (nicht kürzen)')
    parser.add_argument('--provider', '-p', default='webde',
                       choices=['webde', 'gmail', 'gmx', 'custom'],
                       help='E-Mail Provider (Default: webde)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Detaillierte Ausgabe')
    
    args = parser.parse_args()
    
    load_env_file()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Ordner auflisten
    if args.folders:
        folders = list_folders(args.provider)
        print("📁 Verfügbare Ordner:")
        for f in folders:
            print(f"  • {f}")
        return
    
    # E-Mails lesen
    unread_only = args.unread or (not args.all)
    
    emails = read_emails(
        provider=args.provider,
        folder=args.folder,
        unread_only=unread_only,
        limit=args.limit,
        search_subject=args.subject,
        search_from=args.search_from,
        since_days=args.since,
        mark_read=args.mark_read,
    )
    
    if not emails:
        print("📭 Keine E-Mails gefunden.")
        return
    
    # Ausgabe
    if args.json:
        print(emails_to_json(emails))
    else:
        max_body = 999999 if args.full else 200
        print(summarize_emails(emails, max_body_length=max_body))


if __name__ == '__main__':
    main()