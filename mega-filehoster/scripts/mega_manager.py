#!/usr/bin/env python3
"""
MEGA.nz File Manager
Wrapper um megatools für einfache Bedienung
"""

import os
import sys
import subprocess
from pathlib import Path

# Credentials aus .env
MEGA_EMAIL = os.environ.get("MEGA_EMAIL", "")
MEGA_PASSWORD = os.environ.get("MEGA_PASSWORD", "")

def run_mega(cmd, *args):
    """Führt mega-Befehl aus"""
    if not MEGA_EMAIL or not MEGA_PASSWORD:
        print("❌ MEGA_EMAIL und MEGA_PASSWORD in .env setzen!")
        return False
    
    full_cmd = [cmd, "--username", MEGA_EMAIL, "--password", MEGA_PASSWORD] + list(args)
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"❌ Fehler: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def upload(local_path, remote_path="/"):
    """Datei zu MEGA hochladen"""
    print(f"📤 Lade {local_path} zu MEGA hoch...")
    result = run_mega("megaput", local_path, f"{remote_path}{Path(local_path).name}")
    if result:
        print(f"✅ Erfolgreich hochgeladen!")
    return result

def download(remote_path, local_dir="/tmp"):
    """Datei von MEGA herunterladen"""
    print(f"📥 Lade {remote_path} herunter...")
    result = run_mega("megaget", remote_path, local_dir)
    if result:
        print(f"✅ Erfolgreich heruntergeladen!")
    return result

def list_files(remote_path="/"):
    """Verzeichnis auflisten"""
    print(f"📁 Inhalt von {remote_path}:")
    result = run_mega("megals", remote_path)
    if result:
        print(result)
    return result

def quota():
    """Speicherplatz anzeigen"""
    print("💾 Speicherplatz:")
    result = run_mega("megadf", "-h")
    if result:
        print(result)
    return result

def main():
    if len(sys.argv) < 2:
        print("""
MEGA.nz File Manager

Nutzung:
  python3 mega_manager.py upload /pfad/zur/datei [remote_pfad]
  python3 mega_manager.py download /mega/pfad/datei [lokal_pfad]
  python3 mega_manager.py list [remote_pfad]
  python3 mega_manager.py quota

Beispiele:
  python3 mega_manager.py upload /home/user/dokument.pdf
  python3 mega_manager.py download /Backups/wichtig.zip /tmp/
  python3 mega_manager.py list /
  python3 mega_manager.py quota
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "upload":
        if len(sys.argv) < 3:
            print("❌ Dateipfad angeben!")
            sys.exit(1)
        upload(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "/")
    
    elif cmd == "download":
        if len(sys.argv) < 3:
            print("❌ Remote-Pfad angeben!")
            sys.exit(1)
        download(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "/tmp")
    
    elif cmd == "list":
        list_files(sys.argv[2] if len(sys.argv) > 2 else "/")
    
    elif cmd == "quota":
        quota()
    
    else:
        print(f"❌ Unbekannter Befehl: {cmd}")

if __name__ == "__main__":
    main()
