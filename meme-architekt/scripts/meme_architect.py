#!/usr/bin/env python3
"""
Context-Aware Meme Architect
Erstellt Memes basierend auf Gesprächskontext und Emotion
Nutzt imgflip API für echte Meme-Templates
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# imgflip API Konfiguration aus .env
IMGFLIP_USERNAME = os.environ.get("IMGFLIP_USERNAME", "")
IMGFLIP_PASSWORD = os.environ.get("IMGFLIP_PASSWORD", "")

# Template ID Mapping (imgflip Template IDs)
IMGFLIP_TEMPLATES = {
    "success_kid": 61544,
    "distracted_boyfriend": 112126428,
    "two_buttons": 87743020,
    "drake_pointing": 181913649,
    "this_is_fine": 55311130,
    "crying_wolverine": 91538330,
}

# Emotions-Mapping zu Templates
EMOTION_TEMPLATES = {
    "success": {
        "template": "success_kid",
        "default_top": "Endlich...",
        "default_bottom": "Es funktioniert!",
    },
    "frustration": {
        "template": "this_is_fine",
        "default_top": "Alles läuft",
        "default_bottom": "(nicht)",
    },
    "irony": {
        "template": "distracted_boyfriend",
        "default_top": "Ich: Nur noch ein kleiner Fix",
        "default_bottom": "Auch ich: *baut 47 Skills*",
    },
}

def get_popular_templates():
    """Holt alle verfügbaren Templates von imgflip (100+)"""
    url = "https://api.imgflip.com/get_memes"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            if data.get("success"):
                return data["data"]["memes"]
            return []
    except Exception as e:
        print(f"❌ Konnte Templates nicht laden: {e}")
        return []

def search_template(query):
    """Sucht nach Templates via imgflip API"""
    templates = get_popular_templates()
    query_lower = query.lower()
    
    matches = []
    for t in templates:
        if query_lower in t['name'].lower():
            matches.append(t)
    
    return matches[:10]

def create_imgflip_meme(template_id, text_top, text_bottom, output_path):
    """Erstellt ein Meme über die imgflip API mit curl"""
    
    if not IMGFLIP_USERNAME or not IMGFLIP_PASSWORD:
        print("⚠️  Keine imgflip Credentials in .env gefunden!")
        return None
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.imgflip.com/caption_image",
        "-d", f"template_id={template_id}",
        "-d", f"username={IMGFLIP_USERNAME}",
        "-d", f"password={IMGFLIP_PASSWORD}",
        "-d", f"text0={text_top}",
        "-d", f"text1={text_bottom}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        
        if data.get("success"):
            image_url = data["data"]["url"]
            urllib.request.urlretrieve(image_url, output_path)
            print(f"✅ Meme erstellt: {image_url}")
            return output_path
        else:
            print(f"❌ imgflip Fehler: {data.get('error_message', 'Unbekannt')}")
            return None
            
    except Exception as e:
        print(f"❌ Fehler bei imgflip API: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("""
🎩 Context-Aware Meme Architect

Nutzung:
  python3 meme_architect.py "Dein Text hier"           # Automatisches Meme
  python3 meme_architect.py --search "drake"           # Templates suchen
  python3 meme_architect.py --create 181913649 "Oben" "Unten"  # Eigenes Template
  python3 meme_architect.py --list                     # Alle Templates anzeigen
  python3 meme_architect.py --demo                     # Demo-Modus

Beispiele:
  python3 meme_architect.py "Mein Code kompiliert endlich"
  python3 meme_architect.py --search "success"
  python3 meme_architect.py --create 61544 "Endlich" "Es klappt"

Konfiguration:
  Füge zu .env hinzu: IMGFLIP_USERNAME + IMGFLIP_PASSWORD
""")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        print("🎨 Lade alle verfügbaren Templates...")
        templates = get_popular_templates()
        if templates:
            print(f"\n✅ {len(templates)} Templates gefunden!\n")
            print(f"{'ID':<12} {'Name':<35} {'Boxen'}")
            print("-" * 60)
            for t in templates[:20]:
                print(f"{t['id']:<12} {t['name'][:34]:<35} {t.get('box_count', 2)}")
            print(f"\n💡 Zeige alle mit: --search '*'")
        else:
            print("❌ Konnte Templates nicht laden")
        sys.exit(0)
    
    elif sys.argv[1] == "--search":
        if len(sys.argv) < 3:
            print("❌ Bitte Suchbegriff angeben!")
            print("Nutzung: --search 'drake'")
            sys.exit(1)
        
        query = sys.argv[2]
        print(f"🔍 Suche nach '{query}'...")
        results = search_template(query)
        
        if results:
            print(f"\n✅ {len(results)} Templates gefunden:\n")
            print(f"{'ID':<12} {'Name':<35} {'Boxen'}")
            print("-" * 60)
            for t in results:
                print(f"{t['id']:<12} {t['name'][:34]:<35} {t.get('box_count', 2)}")
            print(f"\n💡 Nutze: --create {results[0]['id']} \"Text oben\" \"Text unten\"")
        else:
            print("❌ Keine Templates gefunden")
        sys.exit(0)
    
    elif sys.argv[1] == "--create":
        if len(sys.argv) < 5:
            print("❌ Zu wenige Argumente!")
            print("Nutzung: --create <template_id> \"Text oben\" \"Text unten\"")
            sys.exit(1)
        
        template_id = sys.argv[2]
        text_top = sys.argv[3]
        text_bottom = sys.argv[4]
        output = f"/tmp/meme_{template_id}.png"
        
        print(f"🎨 Erstelle Meme mit Template {template_id}...")
        print(f"   Oben: {text_top}")
        print(f"   Unten: {text_bottom}")
        
        result = create_imgflip_meme(template_id, text_top, text_bottom, output)
        
        if result:
            print(f"\n✅ Meme gespeichert: {result}")
        else:
            print("❌ Fehler beim Erstellen")
        sys.exit(0)
    
    elif sys.argv[1] == "--demo":
        print("🎨 DEMO: Erstelle Beispiel-Memes\n")
        examples = [
            ("181913649", "Manuell arbeiten", "Automatisieren"),
            ("61544", "Endlich", "Es funktioniert!"),
            ("55311130", "Alles läuft", "(nicht)"),
        ]
        
        for template_id, top, bottom in examples:
            print(f"\n📝 Template {template_id}:")
            print(f"   '{top}' / '{bottom}'")
        sys.exit(0)
    
    # Context-basiertes Meme (Default)
    context = sys.argv[1]
    print(f"🎭 Input: {context}")
    print("   Nutze --search oder --create für mehr Kontrolle!")
    print("   Oder: --list für alle verfügbaren Templates")

if __name__ == "__main__":
    main()
