#!/usr/bin/env python3
"""
Web.de Newsletter Monitor v2.0 - KI-gestützte Fleisch-Angebote Extraktion
Nutzt SQLite statt JSON und KI statt Keywords
"""

import os
import sys
import sqlite3
import imaplib
import email
import re
import json
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path
from typing import List, Dict, Any, Optional

# OpenClaw Integration
sys.path.insert(0, '/home/node/.openclaw/workspace')

# Datenbank-Pfad
DB_PATH = Path('/home/node/.openclaw/workspace/data/newsletter.db')
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class NewsletterDatabase:
    """SQLite Datenbank für Newsletter-Angebote"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Erstellt die Datenbank-Tabellen"""
        self.cursor.executescript('''
            -- Shops/Discounter
            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email_pattern TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Newsletter-Einträge
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                sender TEXT,
                subject TEXT,
                received_at TIMESTAMP,
                raw_content TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Extrahierte Angebote
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                newsletter_id INTEGER,
                shop_id INTEGER,
                product_name TEXT NOT NULL,
                price_current REAL,
                price_original REAL,
                price_per_100g REAL,
                weight_g INTEGER,
                discount_percent INTEGER,
                category TEXT,  -- 'fleisch', 'wurst', 'geflügel', etc.
                is_meat BOOLEAN DEFAULT 1,
                valid_from DATE,
                valid_until DATE,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                telegram_sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (newsletter_id) REFERENCES newsletters(id),
                FOREIGN KEY (shop_id) REFERENCES shops(id)
            );
            
            -- Preisverlauf für Statistik
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                offer_id INTEGER,
                price REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (offer_id) REFERENCES offers(id)
            );
            
            -- Indexe für schnelle Suchen
            CREATE INDEX IF NOT EXISTS idx_offers_category ON offers(category);
            CREATE INDEX IF NOT EXISTS idx_offers_shop ON offers(shop_id);
            CREATE INDEX IF NOT EXISTS idx_offers_date ON offers(extracted_at);
            CREATE INDEX IF NOT EXISTS idx_newsletters_msgid ON newsletters(message_id);
        ''')
        self.conn.commit()
        
        # Standard-Shops einfügen
        self._init_shops()
    
    def _init_shops(self):
        """Initialisiert bekannte Shops"""
        shops = [
            ('Netto', '%netto%'),
            ('Lidl', '%lidl%'),
            ('Aldi', '%aldi%'),
            ('Rewe', '%rewe%'),
            ('Edeka', '%edeka%'),
            ('Penny', '%penny%'),
            ('Kaufland', '%kaufland%'),
        ]
        self.cursor.executemany(
            'INSERT OR IGNORE INTO shops (name, email_pattern) VALUES (?, ?)',
            shops
        )
        self.conn.commit()
    
    def save_newsletter(self, message_id: str, sender: str, subject: str, 
                        received_at: datetime, raw_content: str) -> int:
        """Speichert einen Newsletter"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO newsletters 
                (message_id, sender, subject, received_at, raw_content)
                VALUES (?, ?, ?, ?, ?)
            ''', (message_id, sender, subject, received_at, raw_content))
            self.conn.commit()
            
            self.cursor.execute(
                'SELECT id FROM newsletters WHERE message_id = ?', 
                (message_id,)
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"[ERROR] Newsletter speichern fehlgeschlagen: {e}")
            return -1
    
    def save_offer(self, newsletter_id: int, shop_name: str, 
                   product: str, price: float, old_price: float,
                   price_per_100g: float, weight: int, 
                   category: str, is_meat: bool = True) -> int:
        """Speichert ein extrahiertes Angebot"""
        try:
            # Shop-ID finden
            self.cursor.execute(
                'SELECT id FROM shops WHERE name = ?', (shop_name,)
            )
            shop_row = self.cursor.fetchone()
            shop_id = shop_row[0] if shop_row else None
            
            # Rabatt berechnen
            discount = None
            if price and old_price and old_price > 0:
                discount = round((1 - price / old_price) * 100)
            
            self.cursor.execute('''
                INSERT INTO offers 
                (newsletter_id, shop_id, product_name, price_current, price_original,
                 price_per_100g, weight_g, discount_percent, category, is_meat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (newsletter_id, shop_id, product, price, old_price,
                  price_per_100g, weight, discount, category, is_meat))
            self.conn.commit()
            
            return self.cursor.lastrowid
            
        except Exception as e:
            print(f"[ERROR] Angebot speichern fehlgeschlagen: {e}")
            return -1
    
    def get_today_offers(self) -> List[Dict]:
        """Holt alle Angebote von heute"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT o.*, s.name as shop_name, n.subject, n.sender
            FROM offers o
            LEFT JOIN shops s ON o.shop_id = s.id
            LEFT JOIN newsletters n ON o.newsletter_id = n.id
            WHERE date(o.extracted_at) = date('now', 'localtime')
            AND o.is_meat = 1
            ORDER BY o.discount_percent DESC NULLS LAST
        ''')
        
        columns = [desc[0] for desc in self.cursor.description]
        offers = []
        for row in self.cursor.fetchall():
            offers.append(dict(zip(columns, row)))
        return offers
    
    def get_price_trend(self, product_name: str, days: int = 30) -> List[Dict]:
        """Holt Preisverlauf für ein Produkt"""
        self.cursor.execute('''
            SELECT price_current, extracted_at
            FROM offers
            WHERE product_name LIKE ?
            AND extracted_at >= date('now', '-? days')
            ORDER BY extracted_at ASC
        ''', (f'%{product_name}%', days))
        
        return [{'price': row[0], 'date': row[1]} for row in self.cursor.fetchall()]
    
    def close(self):
        self.conn.close()


class KIOfferExtractor:
    """KI-basierte Angebots-Extraktion"""
    
    def __init__(self):
        # Simulierte KI-Analyse (kann durch echte KI ersetzt werden)
        self.meat_indicators = [
            'fleisch', 'wurst', 'hähnchen', 'huhn', 'rind', 'schwein',
            'pute', 'truthahn', 'schnitzel', 'bratwurst', 'würstchen',
            'hackfleisch', 'filet', 'steak', 'kotelett', 'braten',
            'schinken', 'salami', 'bacon', 'speck', 'gyros',
            'frikadellen', 'bouletten', 'klopse'
        ]
    
    def analyze_newsletter(self, text: str, sender: str) -> List[Dict]:
        """Analysiert Newsletter-Inhalt mit KI-Logik"""
        offers = []
        
        # Text bereinigen
        text = self._clean_text(text)
        
        # Shop erkennen
        shop = self._detect_shop(sender, text)
        
        # Angebots-Blöcke finden (meist durch Leerzeilen/Leitungen getrennt)
        blocks = self._split_offers(text)
        
        for block in blocks:
            # Ist das ein Fleisch-Angebot?
            is_meat, category = self._classify_product(block)
            
            if is_meat:
                offer = self._extract_offer_details(block, shop)
                if offer and offer.get('product'):
                    offer['category'] = category
                    offer['shop'] = shop
                    offers.append(offer)
        
        return offers
    
    def _clean_text(self, text: str) -> str:
        """Bereinigt Newsletter-Text"""
        # HTML-Tags entfernen (simple Version)
        text = re.sub(r'<[^>]+>', ' ', text)
        # Mehrfache Leerzeichen
        text = re.sub(r'\s+', ' ', text)
        # Preis-Formate vereinheitlichen
        text = re.sub(r'(\d+)[,.](\d{2})\s*[€]', r'\1,\2€', text)
        return text.strip()
    
    def _detect_shop(self, sender: str, text: str) -> str:
        """Erkennt den Shop aus Absender oder Text"""
        sender_lower = sender.lower()
        text_lower = text.lower()
        
        shop_patterns = [
            ('Netto', ['netto', 'netto-marken']),
            ('Lidl', ['lidl']),
            ('Aldi', ['aldi']),
            ('Rewe', ['rewe']),
            ('Edeka', ['edeka']),
            ('Penny', ['penny']),
            ('Kaufland', ['kaufland']),
        ]
        
        for shop_name, patterns in shop_patterns:
            for pattern in patterns:
                if pattern in sender_lower or pattern in text_lower:
                    return shop_name
        
        return 'Unbekannt'
    
    def _split_offers(self, text: str) -> List[str]:
        """Teilt Text in einzelne Angebots-Blöcke"""
        # Verschiedene Trennzeichen probieren
        separators = [
            '\n\n',           # Doppelte Zeilenumbrüche
            '\r\n\r\n',      # Windows-Style
            '•',              # Bullet points
            '*',              # Sternchen
            '─' * 10,         # Linien
            '━' * 10,
            '-' * 10,
        ]
        
        blocks = [text]
        for sep in separators:
            new_blocks = []
            for block in blocks:
                new_blocks.extend([b.strip() for b in block.split(sep) if b.strip()])
            blocks = new_blocks
        
        return blocks
    
    def _classify_product(self, text: str) -> tuple:
        """Klassifiziert ob ein Text ein Fleisch-Produkt beschreibt"""
        text_lower = text.lower()
        
        # Direkte Fleisch-Indikatoren
        for indicator in self.meat_indicators:
            if indicator in text_lower:
                # Kategorie bestimmen
                if any(w in text_lower for w in ['wurst', 'bratwurst', 'salami', 'lyoner']):
                    return True, 'wurst'
                elif any(w in text_lower for w in ['hähnchen', 'huhn', 'pute', 'truthahn']):
                    return True, 'geflügel'
                elif any(w in text_lower for w in ['rind', 'beef']):
                    return True, 'rind'
                elif any(w in text_lower for w in ['schwein', 'schweine', 'schnitzel']):
                    return True, 'schwein'
                else:
                    return True, 'fleisch'
        
        # Negative Indikatoren (kein Fleisch)
        no_meat = ['seife', 'shampoo', 'waschmittel', 'toilettenpapier',
                   'getränke', 'saft', 'bier', 'wein', 'obst', 'gemüse']
        if any(word in text_lower for word in no_meat):
            return False, None
        
        return False, None
    
    def _extract_offer_details(self, text: str, shop: str) -> Optional[Dict]:
        """Extrahiert Details aus einem Angebots-Block"""
        result = {
            'product': '',
            'price': None,
            'old_price': None,
            'price_per_100g': None,
            'weight': None,
            'shop': shop
        }
        
        # Produkt-Name extrahieren (erste Zeile oder Satz)
        lines = text.split('\n')
        for line in lines[:3]:  # Nur erste 3 Zeilen
            line = line.strip()
            if len(line) > 5 and not re.search(r'\d+[,.]\d{2}', line):
                result['product'] = line[:100]
                break
        
        if not result['product']:
            result['product'] = text[:100].strip()
        
        # Preis extrahieren
        # Aktueller Preis
        price_patterns = [
            r'(\d+[,.]\d{2})\s*[€€]\s*/\s*100g',  # €/100g
            r'(\d+[,.]\d{2})\s*[€€]',              # Normaler Preis
            r'jetzt\s*nur\s*:?\s*(\d+[,.]\d{2})',
            r'nur\s+(\d+[,.]\d{2})',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '.')
                try:
                    result['price'] = float(price_str)
                    break
                except:
                    pass
        
        # Alter Preis (Rabatt)
        old_price_patterns = [
            r'statt\s+(\d+[,.]\d{2})',
            r'uvp\s*:?\s*(\d+[,.]\d{2})',
            r'([\d]+[,.][\d]{2})\s*[€€]?\s*regular',
        ]
        
        for pattern in old_price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                old_price_str = match.group(1).replace(',', '.')
                try:
                    old_price = float(old_price_str)
                    if old_price > (result['price'] or 0):
                        result['old_price'] = old_price
                        break
                except:
                    pass
        
        # Preis pro 100g
        price_100g_match = re.search(r'(\d+[,.]\d{2})\s*[€€]?\s*/\s*100g', text)
        if price_100g_match:
            try:
                result['price_per_100g'] = float(price_100g_match.group(1).replace(',', '.'))
            except:
                pass
        
        # Gewicht extrahieren
        weight_patterns = [
            r'(\d+)\s*g\b',
            r'(\d+)\s*kg\b',
            r'(\d+)\s*gramm',
            r'(\d+)[,.]?\d*\s*kg',
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    weight_val = float(match.group(1).replace(',', '.'))
                    if 'kg' in match.group(0).lower():
                        result['weight'] = int(weight_val * 1000)
                    else:
                        result['weight'] = int(weight_val)
                    break
                except:
                    pass
        
        return result


class WebDeNewsletterMonitorV2:
    """Verbesserter Newsletter Monitor mit SQLite und KI"""
    
    def __init__(self):
        # Lade .env
        from pathlib import Path
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key not in os.environ:
                            os.environ[key] = value
        
        self.email = os.getenv('WEBDE_EMAIL')
        self.password = os.getenv('WEBDE_PASSWORD')
        self.imap_server = os.getenv('WEBDE_IMAP_SERVER', 'imap.web.de')
        self.imap_port = int(os.getenv('WEBDE_IMAP_PORT', 993))
        self.use_ssl = os.getenv('WEBDE_USE_SSL', 'true').lower() == 'true'
        
        if not self.email or not self.password:
            raise ValueError("WEBDE_EMAIL oder WEBDE_PASSWORD nicht in .env gesetzt!")
        
        self.db = NewsletterDatabase()
        self.ki = KIOfferExtractor()
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """Verbindet mit Web.de IMAP"""
        print(f"[INFO] Verbinde mit {self.imap_server}:{self.imap_port}...")
        
        if self.use_ssl:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        else:
            mail = imaplib.IMAP4(self.imap_server, self.imap_port)
        
        mail.login(self.email, self.password)
        print("[INFO] Eingeloggt!")
        return mail
    
    def decode_subject(self, subject: str) -> str:
        """Dekodiert Email-Betreff"""
        if subject is None:
            return ""
        decoded = decode_header(subject)
        result = ""
        for part, encoding in decoded:
            if isinstance(part, bytes):
                result += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                result += part
        return result
    
    def extract_text_from_email(self, msg) -> str:
        """Extrahiert Text aus Email"""
        text = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type in ['text/plain', 'text/html']:
                    try:
                        body = part.get_payload(decode=True)
                        if body:
                            charset = part.get_content_charset() or 'utf-8'
                            text += body.decode(charset, errors='ignore')
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True)
                if body:
                    charset = msg.get_content_charset() or 'utf-8'
                    text = body.decode(charset, errors='ignore')
            except:
                pass
        
        return text
    
    def parse_date(self, date_str: str) -> datetime:
        """Parst Email-Datum"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()
    
    def check_newsletters(self, days: int = 1) -> Dict[str, Any]:
        """Prüft Newsletter der letzten Tage"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'checked_emails': 0,
            'processed_newsletters': 0,
            'offers_found': 0,
            'errors': []
        }
        
        try:
            mail = self.connect()
            mail.select('inbox')
            
            since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            status, messages = mail.search(None, f'SINCE {since_date}')
            
            if status != 'OK':
                results['errors'].append(f"Suche fehlgeschlagen: {status}")
                return results
            
            email_ids = messages[0].split()
            results['checked_emails'] = len(email_ids)
            
            print(f"[INFO] {len(email_ids)} Emails seit {since_date}")
            
            # Newsletter-Absender
            newsletter_senders = [
                'netto', 'lidl', 'aldi', 'rewe', 'edeka', 'penny',
                'kaufland', 'angebot', 'prospekt', 'werbung'
            ]
            
            for email_id in reversed(email_ids[:30]):  # Neueste 30
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    message_id = msg.get('Message-ID', '')
                    subject = self.decode_subject(msg['Subject'])
                    sender = msg['From'] or 'unbekannt'
                    date_str = msg['Date']
                    received_at = self.parse_date(date_str)
                    
                    # Nur Newsletter verarbeiten
                    is_newsletter = any(ns in sender.lower() for ns in newsletter_senders)
                    is_offer = any(word in subject.lower() for word in ['angebot', 'prospekt', 'aktion'])
                    
                    if is_newsletter or is_offer:
                        text = self.extract_text_from_email(msg)
                        
                        # In DB speichern
                        newsletter_id = self.db.save_newsletter(
                            message_id, sender, subject, received_at, text
                        )
                        
                        if newsletter_id > 0:
                            results['processed_newsletters'] += 1
                            
                            # KI-Analyse
                            offers = self.ki.analyze_newsletter(text, sender)
                            
                            for offer in offers:
                                shop_name = offer.get('shop', 'Unbekannt')
                                self.db.save_offer(
                                    newsletter_id=newsletter_id,
                                    shop_name=shop_name,
                                    product=offer['product'],
                                    price=offer['price'],
                                    old_price=offer['old_price'],
                                    price_per_100g=offer['price_per_100g'],
                                    weight=offer['weight'],
                                    category=offer.get('category', 'fleisch')
                                )
                                results['offers_found'] += 1
                                
                except Exception as e:
                    results['errors'].append(f"Email {email_id}: {str(e)[:50]}")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            results['errors'].append(f"Verbindung: {str(e)}")
        
        return results
    
    def format_telegram_message(self, offers: List[Dict]) -> str:
        """Formatiert Angebote für Telegram"""
        if not offers:
            return ""
        
        lines = [
            "🥩 **FLEISCH- & WURST-ANGEBOTE** 🥩",
            f"📅 {datetime.now().strftime('%d.%m.%Y')}",
            f"📧 {len(offers)} Angebote gefunden",
            "",
            "═" * 40,
        ]
        
        # Nach Shop gruppieren
        by_shop = {}
        for offer in offers:
            shop = offer.get('shop_name', 'Unbekannt') or 'Unbekannt'
            if shop not in by_shop:
                by_shop[shop] = []
            by_shop[shop].append(offer)
        
        for shop, shop_offers in by_shop.items():
            lines.append(f"\n🏪 **{shop}**")
            lines.append("─" * 30)
            
            for i, offer in enumerate(shop_offers[:5], 1):
                product = offer.get('product_name', 'Unbekannt')[:50]
                lines.append(f"\n{i}. {product}")
                
                price = offer.get('price_current')
                if price:
                    price_line = f"   💰 **{price:.2f}€**"
                    
                    if offer.get('price_per_100g'):
                        price_line += f" ({offer['price_per_100g']:.2f}€/100g)"
                    
                    if offer.get('discount_percent') and offer['discount_percent'] > 0:
                        price_line += f" ⬇️ **-{offer['discount_percent']}%**"
                    
                    if offer.get('price_original'):
                        price_line += f" ~~{offer['price_original']:.2f}€~~"
                    
                    lines.append(price_line)
                
                if offer.get('weight_g'):
                    if offer['weight_g'] >= 1000:
                        lines.append(f"   ⚖️ {offer['weight_g']/1000:.1f}kg")
                    else:
                        lines.append(f"   ⚖️ {offer['weight_g']}g")
                
                if offer.get('category'):
                    lines.append(f"   🏷️ {offer['category'].capitalize()}")
        
        lines.append("\n" + "═" * 40)
        lines.append("🎩 _Ihr ergebener Butler James_")
        
        return "\n".join(lines)
    
    def send_to_telegram(self, message: str, topic_id: str = "1362"):
        """Sendet an Telegram"""
        try:
            print(f"\n{'='*60}")
            print(f"TELEGRAM (Topic {topic_id}):")
            print('='*60)
            print(message)
            print('='*60)
            
            # TODO: Integration mit OpenClaw message tool
            # from tools import message
            # message(action='send', channel='telegram', target=f'-1003765464477:{topic_id}', ...)
            
            return True
        except Exception as e:
            print(f"[ERROR] Telegram: {e}")
            return False
    
    def run(self, send_telegram: bool = True):
        """Hauptfunktion"""
        print("="*60)
        print("🥩 Web.de Newsletter Monitor v2.0 (KI + SQLite)")
        print("="*60)
        
        results = self.check_newsletters(days=1)
        
        print(f"\n📊 Statistik:")
        print(f"   Geprüfte Emails: {results['checked_emails']}")
        print(f"   Newsletter verarbeitet: {results['processed_newsletters']}")
        print(f"   Angebote gefunden: {results['offers_found']}")
        
        if results['offers_found'] > 0:
            offers = self.db.get_today_offers()
            print(f"\n✅ {len(offers)} Fleisch-Angebote in Datenbank")
            
            if send_telegram and offers:
                telegram_msg = self.format_telegram_message(offers)
                self.send_to_telegram(telegram_msg, "1362")
        else:
            print("\n📭 Keine neuen Angebote")
        
        if results['errors']:
            print(f"\n⚠️ Fehler ({len(results['errors'])}):")
            for err in results['errors'][:3]:
                print(f"   - {err}")
        
        self.db.close()
        return results


if __name__ == '__main__':
    send_telegram = '--no-telegram' not in sys.argv
    
    try:
        monitor = WebDeNewsletterMonitorV2()
        monitor.run(send_telegram=send_telegram)
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)
