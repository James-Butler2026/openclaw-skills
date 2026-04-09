#!/usr/bin/env python3
"""
Context-Aware Meme Architect
Erstellt Memes basierend auf Text-Kontext
"""

import os
import sys
import json
import random
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import urllib.request
import urllib.parse

# Verfügbare Meme-Templates mit Keywords
MEME_TEMPLATES = {
    'success-kid': {
        'id': '61544',
        'name': 'Success Kid',
        'keywords': ['erfolg', 'geschafft', 'endlich', 'läuft', 'build', 'deploy', 'funktioniert', 'sieg'],
        'top_text': 'YES',
        'bottom_text': 'SUCH SUCCESS'
    },
    'distracted-boyfriend': {
        'id': '112126428',
        'name': 'Distracted Boyfriend',
        'keywords': ['neu', 'anderes', 'ablenkung', 'stattdessen', 'nicht mehr', 'wechsel', 'update'],
        'top_text': 'CURRENT PROJECT',
        'bottom_text': 'NEW SHINY PROJECT'
    },
    'two-buttons': {
        'id': '87743020',
        'name': 'Two Buttons',
        'keywords': ['entscheidung', 'oder', 'vs', 'dilemma', 'schwierig', 'wahl', 'feature'],
        'top_text': 'OPTION A',
        'bottom_text': 'OPTION B'
    },
    'drake': {
        'id': '181913649',
        'name': 'Drake Hotline Bling',
        'keywords': ['nein', 'doch', 'besser', 'upgrade', 'alt', 'neu', 'statt'],
        'top_text': 'OLD WAY',
        'bottom_text': 'NEW WAY'
    },
    'change-my-mind': {
        'id': '129242436',
        'name': 'Change My Mind',
        'keywords': ['meinung', 'eigentlich', 'theorie', 'denke', 'glaube', 'überzeugung'],
        'top_text': 'CHANGE MY MIND',
        'bottom_text': ''
    },
    'expanding-brain': {
        'id': '93895088',
        'name': 'Expanding Brain',
        'keywords': ['verstehen', 'erkenntnis', 'aha', 'level', 'advanced', 'profi', 'meister'],
        'top_text': 'NORMAL',
        'bottom_text': 'ENLIGHTENED'
    },
    'roll-safe': {
        'id': '89370399',
        'name': 'Roll Safe',
        'keywords': ['kann nicht', 'wenn man', 'trick', 'schlau', 'loophole', 'life hack', 'genial'],
        'top_text': "CAN'T HAVE BUGS",
        'bottom_text': 'IF YOU WRITE NO CODE'
    },
    'mocking-spongebob': {
        'id': '102156234',
        'name': 'Mocking Spongebob',
        'keywords': ['sarkasmus', 'spott', 'ironie', 'natürlich', 'klar', 'obviously', 'sicher'],
        'top_text': 'sArCaSm',
        'bottom_text': 'mOcKiNg'
    },
    'woman-yelling-cat': {
        'id': '188390779',
        'name': 'Woman Yelling at Cat',
        'keywords': ['streit', 'diskussion', 'verwirrt', 'hä?', 'aber', 'warum', 'konflikt'],
        'top_text': 'WOMAN',
        'bottom_text': 'CAT'
    },
    'always-has-been': {
        'id': '216951317',
        'name': 'Always Has Been',
        'keywords': ['immer', 'schon immer', 'offensichtlich', 'eigentlich', 'wartet', 'astronaut'],
        'top_text': 'WAIT, IT ALL...',
        'bottom_text': 'ALWAYS HAS BEEN'
    }
}

def load_config():
    """Lädt imgflip Credentials aus .env"""
    env_path = Path.home() / '.openclaw' / 'workspace' / '.env'
    config = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    return config

def analyze_text(text):
    """Analysiert Text und wählt passendes Template"""
    text_lower = text.lower()
    
    scores = {}
    for template_id, template in MEME_TEMPLATES.items():
        score = 0
        for keyword in template['keywords']:
            if keyword in text_lower:
                score += 1
        scores[template_id] = score
    
    # Template mit höchstem Score wählen
    best_template = max(scores, key=scores.get)
    
    # Wenn kein Keyword gefunden, zufällig wählen
    if scores[best_template] == 0:
        best_template = random.choice(list(MEME_TEMPLATES.keys()))
    
    return best_template

def create_meme_locally(template_id, top_text, bottom_text, output_path):
    """Erstellt Meme lokal mit Fallback-Template"""
    
    # Bild-Größe
    width, height = 800, 600
    
    # Fallback: Einfaches farbiges Bild erstellen
    bg_colors = {
        'success-kid': (76, 175, 80),  # Grün
        'distracted-boyfriend': (244, 67, 54),  # Rot
        'two-buttons': (255, 152, 0),  # Orange
        'drake': (103, 58, 183),  # Lila
        'change-my-mind': (63, 81, 181),  # Indigo
        'expanding-brain': (0, 150, 136),  # Türkis
        'roll-safe': (255, 193, 7),  # Gelb
        'mocking-spongebob': (255, 235, 59),  # Hellgelb
        'woman-yelling-cat': (233, 30, 99),  # Pink
        'always-has-been': (33, 150, 243)  # Blau
    }
    
    color = bg_colors.get(template_id, (100, 100, 100))
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Versuche Impact-Schriftart zu laden
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_large = ImageFont.load_default()
        font_small = font_large
    
    # Text zeichnen
    # Oben
    top_wrapped = textwrap.fill(top_text.upper(), width=25)
    draw.text((width//2, 50), top_wrapped, fill='white', font=font_large, 
              anchor='mt', stroke_width=3, stroke_fill='black')
    
    # Unten
    bottom_wrapped = textwrap.fill(bottom_text.upper(), width=25)
    draw.text((width//2, height - 50), bottom_wrapped, fill='white', font=font_large,
              anchor='mb', stroke_width=3, stroke_fill='black')
    
    # Template-Namen in Mitte
    template_name = MEME_TEMPLATES.get(template_id, {}).get('name', 'MEME')
    draw.text((width//2, height//2), f"[{template_name}]", fill='white', font=font_small,
              anchor='mm', stroke_width=2, stroke_fill='black')
    
    # Speichern
    img.save(output_path)
    return output_path

def create_meme_imgflip(template_id, top_text, bottom_text):
    """Erstellt Meme via imgflip API"""
    config = load_config()
    
    url = "https://api.imgflip.com/caption_image"
    
    data = {
        'template_id': MEME_TEMPLATES[template_id]['id'],
        'username': config.get('IMGFLIP_USERNAME', ''),
        'password': config.get('IMGFLIP_PASSWORD', ''),
        'text0': top_text.upper(),
        'text1': bottom_text.upper()
    }
    
    # Ohne Credentials: Anonymous API nutzen
    if not data['username']:
        data.pop('username')
        data.pop('password')
        url = "https://api.imgflip.com/caption_image"
    
    try:
        encoded_data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=encoded_data, method='POST')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                return result['data']['url']
            else:
                print(f"   imgflip Fehler: {result.get('error_message', 'Unbekannt')}")
                return None
    except Exception as e:
        print(f"   imgflip API Fehler: {e}")
        return None

def generate_meme(text, template=None, output_dir="/tmp"):
    """Hauptfunktion: Erstellt Meme aus Text"""
    
    # Template auswählen
    if template and template in MEME_TEMPLATES:
        template_id = template
    else:
        template_id = analyze_text(text)
    
    template_info = MEME_TEMPLATES[template_id]
    
    # Text generieren basierend auf Input
    if len(text) < 20:
        top_text = text
        bottom_text = ""
    else:
        # Text aufteilen
        words = text.split()
        mid = len(words) // 2
        top_text = " ".join(words[:mid])
        bottom_text = " ".join(words[mid:])
    
    # Fallback-Text wenn leer
    if not top_text:
        top_text = template_info['top_text']
    if not bottom_text:
        bottom_text = template_info['bottom_text']
    
    print(f"🎭 Template: {template_info['name']}")
    print(f"   Oben: {top_text[:30]}...")
    print(f"   Unten: {bottom_text[:30]}...")
    
    # Versuche imgflip zuerst
    print("   🔄 Versuche imgflip...")
    imgflip_url = create_meme_imgflip(template_id, top_text, bottom_text)
    
    if imgflip_url:
        print(f"   ✅ imgflip: {imgflip_url}")
        return imgflip_url
    
    # Fallback: Lokale Erstellung
    print("   🎨 Erstelle lokal...")
    output_path = f"{output_dir}/meme_{template_id}_{hash(text) % 10000}.png"
    create_meme_locally(template_id, top_text, bottom_text, output_path)
    print(f"   ✅ Lokal: {output_path}")
    return output_path

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Context-Aware Meme Architect')
    parser.add_argument('text', help='Text für das Meme')
    parser.add_argument('--template', '-t', help='Spezifisches Template verwenden')
    parser.add_argument('--output', '-o', default='/tmp', help='Ausgabe-Verzeichnis')
    
    args = parser.parse_args()
    
    print("🎭 Context-Aware Meme Architect")
    print("=" * 50)
    print(f"📥 Input: {args.text}")
    print()
    
    result = generate_meme(args.text, args.template, args.output)
    
    print()
    print("=" * 50)
    print(f"✅ Meme erstellt!")
    print(f"📁 {result}")

if __name__ == '__main__':
    main()
