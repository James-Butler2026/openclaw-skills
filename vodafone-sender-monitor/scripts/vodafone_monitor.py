#!/usr/bin/env python3
"""
Vodafone Sender Monitor v3 - NUR Enigma2 Datei-Download
Kein HTML-Parsing mehr, nur strukturierte Datei
"""

import sqlite3
import re
import subprocess
from datetime import datetime
from pathlib import Path
import sys

DB_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "vodafone_senders.db"
# Enigma2 Export-URL - strukturierte Daten
URL = "https://helpdesk.vodafonekabelforum.de/sendb/export.php?mode=enigma2&netz=380"

def init_db():
    """Initialisiert die Sender-Datenbank"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            frequency_mhz TEXT,
            service_type TEXT,
            encryption TEXT,
            transponder TEXT,
            first_seen TEXT,
            last_updated TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TEXT,
            total_senders INTEGER,
            new_senders INTEGER,
            status TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def download_enigma2_file():
    """Lädt die Enigma2-Datei herunter - KEIN HTML-PARSING"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '30', URL],
            capture_output=True,
            text=True,
            timeout=35
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        else:
            print(f"❌ Download fehlgeschlagen: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Fehler beim Download: {e}")
        return None

def normalize_transponder_id(tid):
    """Normalisiert Transponder-ID auf Format FFFF0000:1:85 (ohne führende Nullen)"""
    parts = tid.split(':')
    if len(parts) >= 3:
        try:
            p1 = parts[0].upper()
            p2 = str(int(parts[1], 16))  # Entferne führende Nullen
            p3 = str(int(parts[2], 16))
            return f"{p1}:{p2}:{p3}"
        except:
            return tid.upper()
    return tid.upper()

def parse_enigma2_services(content):
    """Parst die Enigma2-Datei - strukturierte Daten"""
    senders = []
    lines = content.split('\n')
    
    # Extrahiere Transponder (Frequenzen) - Mapping normalisierte transponder_id -> frequenz_mhz
    transponders = {}
    in_transponders = False
    current_transponder = None
    current_freq = ''
    
    for line in lines:
        line = line.strip()
        
        if line == 'transponders':
            in_transponders = True
            continue
        if line == '/':
            # Speichere vorherigen Transponder mit Frequenz
            if current_transponder and current_freq:
                transponders[current_transponder] = current_freq
            current_transponder = None
            current_freq = ''
            continue
        if line == 'end':
            in_transponders = False
            continue
        if line == 'services':
            break
        
        if in_transponders:
            # Transponder ID (z.B. ffff0000:0001:0085)
            if re.match(r'^[0-9a-fA-F:]+$', line) and len(line.split(':')) >= 3:
                # Speichere vorherigen wenn vorhanden
                if current_transponder and current_freq:
                    transponders[current_transponder] = current_freq
                current_transponder = normalize_transponder_id(line)
                current_freq = ''
            # Frequenz-Zeile (z.B. c 346000:6900000:2:5:15)
            elif line.startswith('c ') and current_transponder:
                parts = line.split()
                if len(parts) >= 2:
                    freq_khz = parts[1].split(':')[0]
                    # Konvertiere zu MHz (346000 kHz = 346 MHz)
                    try:
                        freq_mhz = int(freq_khz) // 1000
                        current_freq = str(freq_mhz)
                    except ValueError:
                        current_freq = freq_khz
    
    # Speichere letzten Transponder
    if current_transponder and current_freq:
        transponders[current_transponder] = current_freq
    
    # Extrahiere Services (Sender)
    in_services = False
    current_sender = None
    
    for line in lines:
        line = line.strip()
        
        if line == 'services':
            in_services = True
            continue
        if line == 'end':
            if in_services:
                break
        
        if in_services and line:
            # Service-ID Zeile (z.B. 2:FFFF0000:1:85:25:0)
            if re.match(r'^[0-9a-fA-F:]+$', line) and len(line.split(':')) >= 4:
                parts = line.split(':')
                sid = parts[0]
                transponder_raw = ':'.join(parts[1:4])
                transponder = normalize_transponder_id(transponder_raw)
                
                # HD oder SD erkennen (25=HD, 22=SD)
                service_type = 'HD' if len(parts) >= 5 and parts[4] == '25' else 'SD'
                
                current_sender = {
                    'sender_id': sid,
                    'name': '',
                    'frequency_mhz': transponders.get(transponder, ''),
                    'service_type': service_type,
                    'encryption': '',
                    'transponder': transponder
                }
            # Sendername (kommt nach Service-ID)
            elif current_sender and not line.startswith('p:') and not line.startswith('C:'):
                if line and line not in ['..', '...', '....', '']:
                    current_sender['name'] = line
            # Provider/Package Zeile (letzte Zeile für diesen Sender)
            elif line.startswith('p:') and current_sender:
                # Verschlüsselung erkennen
                if 'C:1801' in line or 'C:1722' in line:
                    current_sender['encryption'] = 'verschlüsselt'
                else:
                    current_sender['encryption'] = 'unverschlüsselt'
                
                # Füge Sender hinzu wenn wir einen Namen haben
                if current_sender['name']:
                    senders.append(current_sender)
                current_sender = None
    
    return senders

def check_for_new_senders():
    """Prüft auf neue Sender und speichert sie"""
    init_db()
    
    # 1. Datei herunterladen (KEIN HTML-PARSING)
    content = download_enigma2_file()
    if not content:
        print("❌ Konnte Enigma2-Datei nicht herunterladen")
        return []
    
    # 2. Strukturierte Daten parsen
    current_senders = parse_enigma2_services(content)
    if not current_senders:
        print("❌ Keine Sender in Datei gefunden")
        return []
    
    # 3. Vergleiche mit Datenbank
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Hole bestehende Sender
    cursor.execute("SELECT sender_id, name FROM senders")
    existing = {row[0]: row[1] for row in cursor.fetchall()}
    
    new_senders = []
    now = datetime.now().isoformat()
    
    for sender in current_senders:
        if sender['sender_id'] not in existing:
            # Neuer Sender!
            try:
                cursor.execute("""
                    INSERT INTO senders (sender_id, name, frequency_mhz, service_type, 
                                       encryption, transponder, first_seen, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (sender['sender_id'], sender['name'], sender['frequency_mhz'],
                      sender['service_type'], sender['encryption'], sender['transponder'],
                      now, now))
                new_senders.append(sender)
            except sqlite3.IntegrityError:
                pass  # Duplikat
        else:
            # Update timestamp
            cursor.execute("""
                UPDATE senders SET last_updated = ? WHERE sender_id = ?
            """, (now, sender['sender_id']))
    
    # Speichere Scan-History
    cursor.execute("""
        INSERT INTO scan_history (scan_date, total_senders, new_senders, status)
        VALUES (?, ?, ?, ?)
    """, (now, len(current_senders), len(new_senders), 'success'))
    
    conn.commit()
    conn.close()
    
    return new_senders

def get_sender_report():
    """Gibt einen Report über alle Sender aus"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM senders")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM senders ORDER BY name LIMIT 20")
    senders = cursor.fetchall()
    
    conn.close()
    
    return total, senders

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--init":
            init_db()
            print("✅ Datenbank initialisiert")
        elif sys.argv[1] == "--scan":
            new = check_for_new_senders()
            if new:
                print(f"🆕 {len(new)} neue Sender gefunden!")
                for s in new[:10]:
                    print(f"  - {s['name']} ({s['frequency_mhz']} MHz, {s['service_type']})")
                if len(new) > 10:
                    print(f"  ... und {len(new) - 10} weitere")
            else:
                print("✅ Keine neuen Sender")
        elif sys.argv[1] == "--list":
            total, senders = get_sender_report()
            print(f"📺 {total} Sender in Datenbank:")
            for s in senders:
                print(f"  {s[2]} ({s[3]} MHz, {s[4]}) - {s[5]}")
            if total > 20:
                print(f"  ... und {total - 20} weitere")
        elif sys.argv[1] == "--cron":
            new = check_for_new_senders()
            if new:
                print(f"🆕 NEUE SENDER GEFUNDEN: {len(new)}")
                for s in new[:50]:  # Zeige bis zu 50 neue
                    print(f"  {s['name']} ({s['frequency_mhz']} MHz)")
                if len(new) > 50:
                    print(f"  ... und {len(new) - 50} weitere")
                sys.exit(0)  # Erfolg
            else:
                sys.exit(1)  # Keine neuen
    else:
        print("Vodafone Sender Monitor v3 (Enigma2 Datei)")
        print("NUR Download, KEIN HTML-Parsing!")
        print("")
        print("Verwendung:")
        print("  --init   - Datenbank erstellen")
        print("  --scan   - Auf neue Sender prüfen")
        print("  --list   - Alle Sender anzeigen")
        print("  --cron   - Cron-Modus")
