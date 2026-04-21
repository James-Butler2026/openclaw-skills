#!/usr/bin/env python3
"""
Context-Aware Meme Architect
Erstellt Memes basierend auf Gesprächskontext und Emotion
Nutzt imgflip API für echte Meme-Templates
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Versuche Pillow zu importieren
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️  Pillow nicht installiert. Nur Text-Modus verfügbar.")

SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
OUTPUT_DIR = Path("/tmp/meme_architect")

# imgflip API Konfiguration
# .env laden
env_path = Path.home() / '.openclaw' / 'workspace' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

IMGFLIP_USERNAME = os.environ.get("IMGFLIP_USERNAME", "")
IMGFLIP_PASSWORD = os.environ.get("IMGFLIP_PASSWORD", "")

# Template ID Mapping (imgflip Template IDs)
IMGFLIP_TEMPLATES = {
    "success_kid": 61544,
    "distracted_boyfriend": 112126428,
    "two_buttons": 87743020,
    "drake_pointing": 181913649,
    "change_my_mind": 129242436,
    "expanding_brain": 93895088,
    "this_is_fine": 55311130,
    "crying_wolverine": 91538330,
    "mocking_spongebob": 102156234,
    "always_has_been": 252600902,
}

# Emotions-Mapping zu Templates
EMOTION_TEMPLATES = {
    "success": {
        "template": "success_kid",
        "default_top": "Endlich...",
        "default_bottom": "Es funktioniert!",
        "color": "#4CAF50"
    },
    "frustration": {
        "template": "this_is_fine",
        "default_top": "Alles läuft",
        "default_bottom": "(nicht)",
        "color": "#FF5722"
    },
    "dilemma": {
        "template": "two_buttons",
        "default_top": "Schlafen",
        "default_bottom": "Noch einen Cron-Job bauen",
        "color": "#9C27B0"
    },
    "superiority": {
        "template": "drake_pointing",
        "default_top": "Manuell arbeiten",
        "default_bottom": "Automatisieren wie ein Boss",
        "color": "#2196F3"
    },
    "irony": {
        "template": "distracted_boyfriend",
        "default_top": "Ich: 'Nur noch ein kleiner Fix'",
        "default_bottom": "Auch ich: *baut 47 Skills*",
        "color": "#FF9800"
    },
    "nostalgia": {
        "template": "crying_wolverine",
        "default_top": "Erinnert sich an die Zeit",
        "default_bottom": "Als wir nur 5 Cron-Jobs hatten",
        "color": "#607D8B"
    }
}

# Trigger-Wörter für Emotionserkennung
EMOTION_TRIGGERS = {
    "success": ["funktioniert", "geschafft", "endlich", "läuft", "fertig", "done", "erfolg", "geht"],
    "frustration": ["down", "fehler", "nicht", "kaputt", "probleme", "error", "bug", "scheiße", "verdammt"],
    "dilemma": ["oder", "vs", "entscheiden", "beides", "wählen", "dilemma"],
    "superiority": ["besser", "stattdessen", "nein", "upgrade", "neu", "baut"],
    "irony": ["toll", "super", "perfekt", "schön", "ironisch", "natürlich", "klar"],
    "nostalgia": ["früher", "damals", "erinnerst", "vorher", "alte zeiten", "früher war"]
}

def analyze_emotion(text):
    """Analysiert den Text und bestimmt die Emotion"""
    text_lower = text.lower()
    
    # Zähle Treffer pro Emotion
    emotion_scores = {}
    for emotion, triggers in EMOTION_TRIGGERS.items():
        score = sum(1 for trigger in triggers if trigger in text_lower)
        if score > 0:
            emotion_scores[emotion] = score
    
    # Fallback: Ironie erkennen bei "super" + negatives Wort
    if "super" in text_lower or "toll" in text_lower:
        negative_words = ["down", "nicht", "fehler", "problem", "kaputt"]
        if any(word in text_lower for word in negative_words):
            emotion_scores["irony"] = emotion_scores.get("irony", 0) + 2
    
    # Wähle höchste Emotion
    if emotion_scores:
        return max(emotion_scores, key=emotion_scores.get)
    
    return "irony"  # Default

def generate_meme_text(context, emotion):
    """Generiert passenden Meme-Text basierend auf Kontext"""
    template_info = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["irony"])
    
    # Nutze llm für bessere Text-Generierung falls verfügbar
    try:
        # Versuche mit lokalen Qwen
        prompt = f"""Erstelle einen kurzen, witzigen Meme-Text für ein "{template_info['template']}" Meme.

Kontext: {context}
Emotion: {emotion}

Gib mir EXAKT zwei Zeilen zurück:
Zeile 1 (Oberer Text, kurz): 
Zeile 2 (Unterer Text, kurz):

Beispiel:
Oberer Text: "Wenn du 47 Cron-Jobs hast"
Unterer Text: "Aber Pollinations ist down"

Dein Text:"""
        
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace')
# Simple Text-Generierung ohne LLM für jetzt
top = "{template_info['default_top']}"
bottom = "{template_info['default_bottom']}"
print(f"Oberer Text: {{top}}")
print(f"Unterer Text: {{bottom}}")
"""],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse Ergebnis
        lines = result.stdout.strip().split('\n')
        top_text = template_info['default_top']
        bottom_text = template_info['default_bottom']
        
        for line in lines:
            if "Oberer Text:" in line or "Zeile 1" in line:
                top_text = line.split(":", 1)[-1].strip().strip('"')
            elif "Unterer Text:" in line or "Zeile 2" in line:
                bottom_text = line.split(":", 1)[-1].strip().strip('"')
        
        return top_text, bottom_text
        
    except Exception as e:
        # Fallback zu Default-Texten
        return template_info['default_top'], template_info['default_bottom']

def create_imgflip_meme(template_id, text_top, text_bottom, output_path):
    """Erstellt ein Meme über die imgflip API mit curl (zuverlässiger)"""
    
    # Ohne Auth geht's nicht
    if not IMGFLIP_USERNAME or not IMGFLIP_PASSWORD:
        print("⚠️  Keine imgflip Credentials in .env gefunden!")
        print("   Erstelle Account bei imgflip.com und setze:")
        print("   IMGFLIP_USERNAME=dein_username")
        print("   IMGFLIP_PASSWORD=dein_passwort")
        return None
    
    # Verwende curl für bessere Kompatibilität
    import subprocess
    
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
            # Lade Bild herunter
            urllib.request.urlretrieve(image_url, output_path)
            print(f"✅ Meme erstellt via imgflip!")
            return output_path
        else:
            error_msg = data.get("error_message", "Unbekannter Fehler")
            print(f"❌ imgflip Fehler: {error_msg}")
            return None
            
    except Exception as e:
        print(f"❌ Fehler bei imgflip API: {e}")
        return None

def get_popular_templates():
    """Holt populäre Templates von imgflip"""
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
    
    # Suche in Namen
    matches = []
    for t in templates:
        if query_lower in t['name'].lower():
            matches.append(t)
    
    return matches[:10]  # Max 10 Ergebnisse

def create_text_meme(text_top, text_bottom, emotion, output_path):
    """Erstellt ein einfaches Text-basiertes Meme"""
    if not PILLOW_AVAILABLE:
        return None
    
    template_info = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["irony"])
    
    # Erstelle Bild mit passender Farbe
    width, height = 800, 600
    bg_color = template_info['color']
    
    # Konvertiere Hex zu RGB
    bg_color = bg_color.lstrip('#')
    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
    
    img = Image.new('RGB', (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)
    
    # Versuche Schriftart zu laden
    try:
        # System-Fonts
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "C:\\Windows\\Fonts\\Arial.ttf",  # Windows
        ]
        
        font_large = None
        for path in font_paths:
            if os.path.exists(path):
                font_large = ImageFont.truetype(path, 48)
                font_small = ImageFont.truetype(path, 36)
                break
        
        if font_large is None:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Zeichne Text
    # Oberer Text
    draw.text((width//2, 80), text_top, fill="white", font=font_large, anchor="mm", stroke_width=2, stroke_fill="black")
    
    # Meme-Name in der Mitte
    meme_name = template_info['template'].replace('_', ' ').upper()
    draw.text((width//2, height//2), f"[ {meme_name} ]", fill="white", font=font_small, anchor="mm", stroke_width=1, stroke_fill="black")
    
    # Unterer Text
    draw.text((width//2, height - 80), text_bottom, fill="white", font=font_large, anchor="mm", stroke_width=2, stroke_fill="black")
    
    # Speichere
    img.save(output_path)
    return output_path

def create_context_meme(context, emotion=None, output_path=None, use_imgflip=True):
    """Hauptfunktion: Erstellt Meme aus Kontext"""

    # Stelle sicher, dass Output-Verzeichnis existiert
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"meme_{timestamp}.png"

    # Analysiere Emotion falls nicht angegeben
    if emotion is None:
        emotion = analyze_emotion(context)

    print(f"🎭 Erkannte Emotion: {emotion}")

    # Generiere Text
    text_top, text_bottom = generate_meme_text(context, emotion)
    print(f"📝 Oberer Text: {text_top}")
    print(f"📝 Unterer Text: {text_bottom}")

    # Wähle Template
    template_key = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["irony"])["template"]
    template_id = IMGFLIP_TEMPLATES.get(template_key, 61544)  # Default: success kid

    # Versuche imgflip API zuerst (wenn gewünscht und Credentials vorhanden)
    if use_imgflip and IMGFLIP_USERNAME and IMGFLIP_PASSWORD:
        print(f"🎨 Erstelle Meme via imgflip API...")
        result = create_imgflip_meme(template_id, text_top, text_bottom, output_path)
        if result:
            print(f"✅ Meme erstellt: {result}")
            return str(result)
        else:
            print("⚠️  imgflip fehlgeschlagen, versuche lokale Erstellung...")

    # Fallback: Lokale Erstellung
    result = create_text_meme(text_top, text_bottom, emotion, output_path)

    if result:
        print(f"✅ Meme erstellt: {result}")
        return str(result)
    else:
        # Fallback: Nur Text ausgeben
        print(f"\n🎨 MEME VORSCHLAG ({emotion.upper()}):")
        print(f"   ┌{'─' * 50}┐")
        print(f"   │ {text_top:^48} │")
        print(f"   │{' ' * 48}│")
        print(f"   │     [ {template_key.replace('_', ' ').upper()} ]")
        print(f"   │{' ' * 48}│")
        print(f"   │ {text_bottom:^48} │")
        print(f"   └{'─' * 50}┘")
        return None

def main():
    if len(sys.argv) < 2:
        print("""
🎩 Context-Aware Meme Architect

Nutzung:
  python3 meme_architect.py "Dein Text hier"
  python3 meme_architect.py "Text" --emotion success
  python3 meme_architect.py --demo
  python3 meme_architect.py --list           # Zeigt verfügbare Templates

Beispiele:
  python3 meme_architect.py "Mein Code kompiliert endlich"
  python3 meme_architect.py "Pollinations ist down aber Supadata läuft" --emotion irony

Verfügbare Emotionen:
  success, frustration, dilemma, superiority, irony, nostalgia

Konfiguration:
  IMGFLIP_USERNAME und IMGFLIP_PASSWORD in .env setzen
  für echte Meme-Templates von imgflip.com
""")
        sys.exit(1)

    # Parse Argumente
    if sys.argv[1] == "--demo":
        # Demo-Modus: Mehrere Beispiele
        examples = [
            ("Endlich! Der Cron-Job läuft seit 3 Tagen ohne Fehler!", None),
            ("Pollinations streikt wieder, aber wenigstens haben wir noch 97 Supadata Credits", None),
            ("Soll ich schlafen oder noch einen Skill bauen?", None),
            ("Erinnert sich noch jemand an die Zeit als wir nur 5 Cron-Jobs hatten?", None),
        ]

        print("🎨 DEMO-MODUS: Erstelle Beispiel-Memes\n")
        for text, emotion in examples:
            print(f"\n{'='*60}")
            print(f"Input: {text}")
            create_context_meme(text, emotion)

        sys.exit(0)

    elif sys.argv[1] == "--list":
        # Liste verfügbare Templates
        print("🎨 Verfügbare Meme-Templates:\n")
        print(f"{'Template':<25} {'imgflip ID':<12} {'Emotion'}")
        print("-" * 55)
        for emotion, info in EMOTION_TEMPLATES.items():
            template = info['template']
            template_id = IMGFLIP_TEMPLATES.get(template, 'N/A')
            print(f"{template:<25} {template_id:<12} {emotion}")
        print("\n💡 Tipp: Erstelle Account bei imgflip.com für echte Meme-Bilder!")
        print("💡 Suche nach Templates: python3 meme_architect.py --search 'drake'")
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
            print(f"\n💡 Nutze: python3 meme_architect.py --create {results[0]['id']} \"Text oben\" \"Text unten\"")
        else:
            print("❌ Keine Templates gefunden")
        sys.exit(0)

    # Parse Template ID (falls --create verwendet)
    if sys.argv[1] == "--create":
        if len(sys.argv) < 5:
            print("❌ Zu wenige Argumente!")
            print("Nutzung: --create <template_id> \"Text oben\" \"Text unten\"")
            sys.exit(1)
        
        template_id = sys.argv[2]
        text_top = sys.argv[3]
        text_bottom = sys.argv[4]
        output = sys.argv[5] if len(sys.argv) > 5 else "/tmp/meme_custom.png"
        
        print(f"🎨 Erstelle Meme mit Template {template_id}...")
        result = create_imgflip_meme(template_id, text_top, text_bottom, output)
        
        if result:
            print(f"✅ Meme erstellt: {result}")
        else:
            print("❌ Fehler beim Erstellen")
        sys.exit(0)
    
    # Normaler Modus (Context-based)
    context = sys.argv[1]
    emotion = None
    use_imgflip = True

    # Parse Flags
    for i, arg in enumerate(sys.argv):
        if arg == "--emotion" and i + 1 < len(sys.argv):
            emotion = sys.argv[i + 1]
        elif arg == "--no-imgflip":
            use_imgflip = False

    # Erstelle Meme
    result = create_context_meme(context, emotion, use_imgflip=use_imgflip)

    if result:
        print(f"\n💾 Gespeichert unter: {result}")

if __name__ == "__main__":
    main()
