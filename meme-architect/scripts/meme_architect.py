#!/usr/bin/env python3
"""
Context-Aware Meme Architect
Erstellt Memes basierend auf Kontext und Emotion.
Nutzt imgflip API für echte Meme-Templates (via curl).

Workflow (--auto):
  1. Analysiere Kontext → Emotion erkennen
  2. Keywords extrahieren (schule, schlaf, arbeit, etc.)
  3. Suche passendes Template in imgflip API (Top 100)
  4. Erstelle Meme mit imgflip API
"""

import os
import sys
import json
import subprocess
import urllib.parse
from datetime import datetime
from pathlib import Path

# Versuche Pillow für Fallback
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path("/tmp/meme_architect")

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

# --- imgflip Template IDs ---
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
    "hide_the_pain_harold": 27813981,
}

# --- Emotion → Template Mapping ---
EMOTION_TEMPLATES = {
    "success":    {"template": "success_kid",           "default_top": "Endlich...",                                "default_bottom": "Es funktioniert!",        "color": "#4CAF50"},
    "frustration": {"template": "this_is_fine",          "default_top": "Alles läuft",                              "default_bottom": "(nicht)",                  "color": "#FF5722"},
    "dilemma":    {"template": "two_buttons",            "default_top": "Schlafen",                                 "default_bottom": "Noch einen Skill bauen",   "color": "#9C27B0"},
    "superiority": {"template": "drake_pointing",         "default_top": "Manuell arbeiten",                         "default_bottom": "Automatisieren wie ein Boss", "color": "#2196F3"},
    "irony":      {"template": "distracted_boyfriend",   "default_top": "Ich: 'Nur noch ein kleiner Fix'",          "default_bottom": "Auch ich: *baut 47 Skills*", "color": "#FF9800"},
    "nostalgia":  {"template": "crying_wolverine",        "default_top": "Erinnert sich an die Zeit",                "default_bottom": "Als wir nur 5 Cron-Jobs hatten", "color": "#607D8B"}
}

# --- Emotions-Erkennung ---
EMOTION_TRIGGERS = {
    "success":    ["funktioniert", "geschafft", "endlich", "läuft", "fertig", "done", "erfolg", "geht"],
    "frustration": ["down", "fehler", "nicht", "kaputt", "probleme", "error", "bug", "scheiße", "verdammt"],
    "dilemma":    ["oder", "vs", "entscheiden", "beides", "wählen", "dilemma"],
    "superiority": ["besser", "stattdessen", "nein", "upgrade", "neu", "baut"],
    "irony":      ["toll", "super", "perfekt", "schön", "ironisch", "natürlich", "klar"],
    "nostalgia":  ["früher", "damals", "erinnerst", "vorher", "alte zeiten", "früher war"]
}

# --- Keyword-Mapping für Template-Suche ---
KEYWORD_TAGS = [
    (["schlaf", "pennen", "müde", "gähnen", "übermüdet", "nacht", "sleep", "tired", "exhausted"], "sleeping"),
    (["schmerz", "wehtun", "kaputt", "erschöpft", "k.o.", "fertig", "pain", "hurt", "sore", "ache", "dead", "die", "dying"], "pain"),
    (["lernen", "schule", "studium", "unterricht", "prüfung", "klausur", "schüler", "study", "exam", "class"], "studying"),
    (["arbeit", "job", "arbeiten", "büro", "kollege", "work", "office", "boss"], "work"),
    (["computer", "code", "programm", "pc", "server", "internet", "bug", "error", "programming"], "computer nerd"),
    (["essen", "hunger", "futter", "pizza", "burger", "küche", "food", "hungry", "kitchen"], "food"),
    (["geld", "arm", "reich", "sparen", "teuer", "gehalt", "money", "poor", "rich", "expensive"], "money"),
    (["sport", "fitness", "gym", "training", "muskel", "workout", "gym", "muscle"], "gym"),
    (["auto", "fahren", "straße", "verkehr", "fahrrad", "car", "drive", "road", "traffic"], "driving"),
    (["frau", "freundin", "mädchen", "liebe", "beziehung", "girl", "girlfriend", "relationship"], "relationship"),
    (["katze", "hund", "tier", "haustier", "cat", "dog", "pet"], "pet"),
    (["krank", "krankheit", "arzt", "doktor", "schnupfen", "sick", "doctor", "hospital"], "sick"),
    (["party", "feiern", "bier", "alkohol", "betrunken", "party", "celebrate", "drunk"], "party"),
    (["spiel", "zocken", "gaming", "ps5", "xbox", "nintendo", "game", "gaming", "play"], "gaming"),
]

def analyze_emotion(text):
    """Erkennt Emotion basierend auf Trigger-Wörtern"""
    text_lower = text.lower()
    emotion_scores = {}

    for emotion, triggers in EMOTION_TRIGGERS.items():
        score = sum(1 for trigger in triggers if trigger in text_lower)
        if score > 0:
            emotion_scores[emotion] = score

    # Ironie: "super/toll" + negatives Wort
    if "super" in text_lower or "toll" in text_lower:
        negative = ["down", "nicht", "fehler", "problem", "kaputt"]
        if any(w in text_lower for w in negative):
            emotion_scores["irony"] = emotion_scores.get("irony", 0) + 2

    return max(emotion_scores, key=emotion_scores.get) if emotion_scores else "irony"

def generate_meme_text(context, emotion):
    """Gibt Default-Text für Emotion zurück, mit一点点 Kontext"""
    info = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["irony"])
    
    # Bei Frustration: nimm ersten Teil des Kontexts als Text
    if emotion == "frustration" and context:
        words = context.split()[:6]
        top = " ".join(words) + ("..." if len(context.split()) > 6 else "")
        return top, info['default_bottom']
    
    return info['default_top'], info['default_bottom']

def extract_keywords(context):
    """Extrahiert Keywords aus Kontext für Template-Suche"""
    context_lower = context.lower()
    found = set()
    for triggers, tag in KEYWORD_TAGS:
        if any(t in context_lower for t in triggers):
            found.add(tag)
    return found

def get_popular_templates():
    """Holt Top 100 Templates von imgflip API"""
    cmd = [
        "curl", "-s",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "https://api.imgflip.com/get_memes"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        return data["data"]["memes"] if data.get("success") else []
    except json.JSONDecodeError:
        return []
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout beim Laden der Templates")
        return []

def search_templates(query):
    """Sucht Templates in imgflip Top 100 nach Query"""
    templates = get_popular_templates()
    query_lower = query.lower()
    return [t for t in templates if query_lower in t['name'].lower()][:15]

def find_best_template(context, emotion=None):
    """Findet passendstes Template via Keyword-Matching + API-Fallback"""
    keywords = extract_keywords(context)
    templates = get_popular_templates()

    candidates = []

    # Keywords matchen (nur EIN Durchlauf, nicht zwei!)
    if keywords:
        for t in templates:
            name_lower = t['name'].lower()
            if any(kw in name_lower for kw in keywords):
                if t not in candidates:  # Keine Duplikate
                    candidates.append(t)

    # Emotion-Template als Fallback
    if not candidates and emotion:
        emotion_info = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["irony"])
        template_key = emotion_info["template"]
        template_id = IMGFLIP_TEMPLATES.get(template_key)
        for t in templates:
            if str(t['id']) == str(template_id):
                candidates.append(t)
                break

    if candidates:
        return candidates[0]

    # Fallback: success kid
    return {"id": 61544, "name": "success kid", "box_count": 2}

def create_imgflip_meme(template_id, text_top, text_bottom, output_path):
    """Erstellt Meme via imgflip API mit curl - MIT SHELL-INJECTION SCHUTZ"""
    if not IMGFLIP_USERNAME or not IMGFLIP_PASSWORD:
        print("⚠️  Keine imgflip Credentials in .env!")
        return None

    # URL-Encode user input to prevent shell injection
    text_top_enc = urllib.parse.quote(text_top, safe='')
    text_bottom_enc = urllib.parse.quote(text_bottom, safe='')

    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.imgflip.com/caption_image",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-d", f"template_id={template_id}",
        "-d", f"username={IMGFLIP_USERNAME}",
        "-d", f"password={IMGFLIP_PASSWORD}",
        "-d", f"text0={text_top_enc}",
        "-d", f"text1={text_bottom_enc}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        if data.get("success"):
            image_url = data["data"]["url"]
            subprocess.run(
                ["curl", "-s", "-L", "-o", output_path,
                 "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                 image_url],
                capture_output=True, timeout=30
            )
            return str(output_path)
    except json.JSONDecodeError:
        print("❌ imgflip: Ungültige Antwort")
    except subprocess.TimeoutExpired:
        print("❌ imgflip: Timeout")
    except subprocess.SubprocessError as e:
        print(f"❌ imgflip Fehler: {e}")
    return None

def create_text_meme(text_top, text_bottom, emotion, output_path):
    """Fallback: Text-Meme mit Pillow"""
    if not PILLOW_AVAILABLE:
        return None
    info = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["irony"])
    bg = info['color'].lstrip('#')
    rgb = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
    img = Image.new('RGB', (800, 600), rgb)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
    except Exception:
        font = ImageFont.load_default()
    draw.text((400, 300), f"{text_top}\n\n{text_bottom}",
              fill="white", font=font, anchor="mm", align="center")
    img.save(output_path)
    return str(output_path)

def create_auto_meme(context, emotion=None, output_path=None):
    """--auto Modus: Automatische Template-Suche + Meme-Erstellung"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = output_path or OUTPUT_DIR / f"meme_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    if not emotion:
        emotion = analyze_emotion(context)

    text_top, text_bottom = generate_meme_text(context, emotion)
    template = find_best_template(context, emotion)
    template_id = template['id']
    template_name = template['name']

    print(f"🎭 Emotion: {emotion}")
    print(f"📝 Text: \"{text_top}\" / \"{text_bottom}\"")
    print(f"🎨 Template: {template_name} (ID: {template_id})")

    if IMGFLIP_USERNAME and IMGFLIP_PASSWORD:
        result = create_imgflip_meme(template_id, text_top, text_bottom, output_path)
        if result:
            print(f"✅ Meme: {result}")
            return result

    return create_text_meme(text_top, text_bottom, emotion, output_path)

def main():
    if len(sys.argv) < 2:
        print("""
🎩 Context-Aware Meme Architect

Nutzung:
  python3 meme_architect.py --auto "Dein Text hier"   # Automatische Suche!
  python3 meme_architect.py "Text" --emotion success  # Manuel
  python3 meme_architect.py --search 'drake'          # Templates suchen
  python3 meme_architect.py --create 61544 "Oben" "Unten"  # Eigenes Template
  python3 meme_architect.py --list                     # Alle Templates
  python3 meme_architect.py --demo                      # Demo-Modus

Emotionen: success, frustration, dilemma, superiority, irony, nostalgia

Beispiel:
  python3 meme_architect.py --auto "3 Monate Schule, heute Prüfung, nichts verstanden"
""")
        sys.exit(1)

    # --demo
    if sys.argv[1] == "--demo":
        for text, _ in [
            ("Endlich! Der Cron-Job läuft ohne Fehler!", None),
            ("Pollinations streikt, aber Supadata läuft", None),
            ("Soll ich schlafen oder noch einen Skill bauen?", None),
            ("Früher hatten wir nur 5 Cron-Jobs...", None),
        ]:
            print(f"\n{'='*50}\nInput: {text}")
            create_auto_meme(text)
        sys.exit(0)

    # --list
    if sys.argv[1] == "--list":
        print("🎨 Templates:\nID         Name                    Emotion")
        print("-" * 55)
        for em, info in EMOTION_TEMPLATES.items():
            tid = IMGFLIP_TEMPLATES.get(info["template"], "N/A")
            print(f"{tid:<10} {info['template']:<22} {em}")
        sys.exit(0)

    # --search
    if sys.argv[1] == "--search":
        if len(sys.argv) < 3:
            print("❌ Nutzung: --search 'begriff'")
            sys.exit(1)
        results = search_templates(sys.argv[2])
        if results:
            print(f"✅ {len(results)} Templates:")
            for t in results:
                print(f"  {t['id']:<12} {t['name'][:35]}")
        else:
            print("❌ Keine gefunden")
        sys.exit(0)

    # --create
    if sys.argv[1] == "--create":
        if len(sys.argv) < 5:
            print("❌ Nutzung: --create <id> \"Oben\" \"Unten\" [output]")
            sys.exit(1)
        tid, top, bottom = sys.argv[2], sys.argv[3], sys.argv[4]
        out = sys.argv[5] if len(sys.argv) > 5 else "/tmp/meme.png"
        result = create_imgflip_meme(tid, top, bottom, out)
        print(f"✅ Meme: {result}" if result else "❌ Fehler")
        sys.exit(0)

    # --auto
    if sys.argv[1] == "--auto":
        if len(sys.argv) < 3:
            print("❌ Nutzung: --auto \"Kontext\"")
            sys.exit(1)
        ctx, em, out = sys.argv[2], None, None
        for i, a in enumerate(sys.argv):
            if a == "--emotion" and i+1 < len(sys.argv): em = sys.argv[i+1]
            if a == "--output" and i+1 < len(sys.argv): out = sys.argv[i+1]
        result = create_auto_meme(ctx, em, out)
        print(f"\n💾 {result}" if result else "❌ Fehler")
        sys.exit(0)

    # Default: Kontext-basiert
    ctx, em, out = sys.argv[1], None, None
    for i, a in enumerate(sys.argv):
        if a == "--emotion" and i+1 < len(sys.argv): em = sys.argv[i+1]
        if a == "--output" and i+1 < len(sys.argv): out = sys.argv[i+1]

    result = create_auto_meme(ctx, em, out)
    print(f"\n💾 {result}" if result else "❌ Fehler")

if __name__ == "__main__":
    main()