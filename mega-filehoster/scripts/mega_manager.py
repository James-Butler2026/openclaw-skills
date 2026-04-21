#!/usr/bin/env python3
"""
MEGA.nz File Manager v2.0
Wrapper um megatools für einfache Bedienung
SICHER: Credentials werden aus Output entfernt
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# .env laden
env_path = Path.home() / '.openclaw' / 'workspace' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Credentials aus .env
MEGA_EMAIL = os.environ.get("MEGA_EMAIL", "")
MEGA_PASSWORD = os.environ.get("MEGA_PASSWORD", "")


def sanitize_output(text):
    """Entfernt Credentials aus Output"""
    if not text:
        return text
    # Email und Passwort ersetzen
    text = text.replace(MEGA_EMAIL, '***EMAIL***')
    text = text.replace(MEGA_PASSWORD, '***PASSWORD***')
    return text


def run_mega(cmd, *args):
    """Führt mega-Befehl aus - sicher"""
    if not MEGA_EMAIL or not MEGA_PASSWORD:
        logger.error("MEGA_EMAIL und MEGA_PASSWORD in .env setzen!")
        return False
    
    full_cmd = [cmd, "--username", MEGA_EMAIL, "--password", MEGA_PASSWORD] + list(args)
    try:
        logger.info(f"🔄 Führe aus: {cmd}")
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            safe_output = sanitize_output(result.stdout)
            return safe_output
        else:
            safe_error = sanitize_output(result.stderr)
            logger.error(f"Fehler: {safe_error}")
            return False
            
    except Exception as e:
        safe_error = sanitize_output(str(e))
        logger.error(f"Exception: {safe_error}")
        return False


def upload(local_path, remote_path="/"):
    """Datei zu MEGA hochladen"""
    local_file = Path(local_path)
    if not local_file.exists():
        logger.error(f"Datei nicht gefunden: {local_path}")
        return False
    
    logger.info(f"📤 Lade {local_file.name} zu MEGA hoch...")
    result = run_mega("megaput", str(local_file), f"{remote_path}{local_file.name}")
    
    if result:
        logger.info("✅ Erfolgreich hochgeladen!")
    return result


def download(remote_path, local_dir="/tmp"):
    """Datei von MEGA herunterladen"""
    logger.info(f"📥 Lade {remote_path} herunter...")
    result = run_mega("megaget", remote_path, local_dir)
    
    if result:
        logger.info("✅ Erfolgreich heruntergeladen!")
    return result


def list_files(remote_path="/"):
    """Verzeichnis auflisten"""
    logger.info(f"📁 Inhalt von {remote_path}:")
    result = run_mega("megals", remote_path)
    
    if result:
        print(result)
    return result


def share(remote_path):
    """Share-Link für Datei erstellen"""
    logger.info(f"🔗 Erstelle Share-Link für {remote_path}...")
    result = run_mega("mega-export", remote_path)
    
    if result:
        logger.info("✅ Share-Link erstellt!")
        print(result)
    return result


def quota():
    """Speicherplatz anzeigen"""
    logger.info("💾 Speicherplatz:")
    result = run_mega("megadf", "-h")
    
    if result:
        print(result)
    return result


def main():
    if len(sys.argv) < 2:
        print("""
MEGA.nz File Manager v2.0

Nutzung:
  python3 mega_manager.py upload /pfad/zur/datei [remote_pfad]
  python3 mega_manager.py download /mega/pfad/datei [lokal_pfad]
  python3 mega_manager.py list [remote_pfad]
  python3 mega_manager.py share /mega/pfad/datei
  python3 mega_manager.py quota

Beispiele:
  python3 mega_manager.py upload /home/user/dokument.pdf
  python3 mega_manager.py download /Backups/wichtig.zip /tmp/
  python3 mega_manager.py list /
  python3 mega_manager.py share /Dokumente/wichtig.pdf
  python3 mega_manager.py quota
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "upload":
        if len(sys.argv) < 3:
            logger.error("Dateipfad angeben!")
            sys.exit(1)
        upload(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "/")
    
    elif cmd == "download":
        if len(sys.argv) < 3:
            logger.error("Remote-Pfad angeben!")
            sys.exit(1)
        download(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "/tmp")
    
    elif cmd == "list":
        list_files(sys.argv[2] if len(sys.argv) > 2 else "/")
    
    elif cmd == "share":
        if len(sys.argv) < 3:
            logger.error("Remote-Pfad angeben!")
            sys.exit(1)
        share(sys.argv[2])
    
    elif cmd == "quota":
        quota()
    
    else:
        logger.error(f"Unbekannter Befehl: {cmd}")


if __name__ == "__main__":
    main()
