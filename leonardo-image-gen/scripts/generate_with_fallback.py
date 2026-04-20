#!/usr/bin/env python3
"""
Bildgenerierung mit automatischem Fallback
Priorität: 1. Pollinations (kostenlos) → 2. Leonardo AI (zuverlässig)
"""

import os
import sys
import argparse
import time
import random
from pathlib import Path
import requests
import urllib.request

# Versuche Leonardo zu importieren
try:
    from leonardo_generate import LeonardoAI
    LEONARDO_AVAILABLE = True
except ImportError:
    LEONARDO_AVAILABLE = False
    print("⚠️  Leonardo AI Modul nicht gefunden. Nur Pollinations wird verwendet.")

def generate_with_pollinations(prompt, width=1024, height=1024, seed=None, output_path=None):
    """
    Generiert Bild via Pollinations.ai (kostenlos)
    """
    if seed is None:
        seed = random.randint(1, 999999)
    
    # URL-encode den Prompt
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Pollinations URL
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
    
    try:
        print("🎨 Versuche Pollinations.ai...")
        
        # Timeout: 30 Sekunden
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Bild speichern
            if output_path is None:
                timestamp = int(time.time())
                output_dir = Path("/home/node/.openclaw/workspace/output")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"pollinations_{timestamp}.png"
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return {
                "success": True,
                "provider": "pollinations",
                "path": output_path,
                "size": len(response.content)
            }
        else:
            return {
                "success": False,
                "provider": "pollinations",
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "provider": "pollinations",
            "error": str(e)
        }

def generate_with_leonardo(prompt, width=1024, height=1024, model="flux-schnell", output_path=None):
    """
    Generiert Bild via Leonardo AI (Fallback)
    """
    if not LEONARDO_AVAILABLE:
        return {
            "success": False,
            "provider": "leonardo",
            "error": "Leonardo AI Modul nicht verfügbar"
        }
    
    try:
        print("🎨 Wechsle zu Leonardo AI...")
        
        client = LeonardoAI()
        
        # Modell ID
        model_id = client.MODELS.get(model, client.MODELS["vision-xl"])
        
        # Bild generieren
        images = client.generate_image(
            prompt=prompt,
            model_id=model_id,
            width=width,
            height=height,
            num_images=1
        )
        
        if images and len(images) > 0:
            img_url = images[0].get("url")
            if img_url:
                # Speichern
                if output_path is None:
                    timestamp = int(time.time())
                    output_dir = Path("/home/node/.openclaw/workspace/output/leonardo")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / f"leonardo_{timestamp}_1.png"
                else:
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                
                client.download_image(img_url, output_path)
                
                return {
                    "success": True,
                    "provider": "leonardo",
                    "path": output_path,
                    "model": model
                }
        
        return {
            "success": False,
            "provider": "leonardo",
            "error": "Keine Bilder generiert"
        }
        
    except Exception as e:
        return {
            "success": False,
            "provider": "leonardo",
            "error": str(e)
        }

def generate_image_with_fallback(prompt, width=1024, height=1024, 
                                  output_path=None, leonardo_model="flux-schnell"):
    """
    Generiert Bild mit automatischem Fallback
    
    Reihenfolge:
    1. Pollinations.ai (kostenlos)
    2. Leonardo AI (zuverlässig, Daily Credits)
    
    Args:
        prompt: Text-Beschreibung
        width: Bildbreite
        height: Bildhöhe
        output_path: Optionaler Ausgabepfad
        leonardo_model: Fallback-Modell für Leonardo
    
    Returns:
        Dict mit success, provider, path, error
    """
    print(f"🎯 Generiere Bild: {prompt[:50]}...")
    print(f"   Auflösung: {width}x{height}")
    print()
    
    start_time = time.time()
    
    # Versuch 1: Pollinations
    result = generate_with_pollinations(prompt, width, height, output_path=output_path)
    
    if result["success"]:
        elapsed = time.time() - start_time
        print(f"✅ Erfolg mit Pollinations! ({elapsed:.1f}s)")
        return result
    
    print(f"⚠️  Pollinations fehlgeschlagen: {result.get('error', 'Unbekannt')}")
    print("   Wechsle zu Leonardo AI...")
    print()
    
    # Versuch 2: Leonardo AI
    result = generate_with_leonardo(prompt, width, height, leonardo_model, output_path)
    
    if result["success"]:
        elapsed = time.time() - start_time
        print(f"✅ Erfolg mit Leonardo AI! ({elapsed:.1f}s)")
        return result
    
    # Beide fehlgeschlagen
    print(f"❌ Beide Anbieter fehlgeschlagen:")
    print(f"   Pollinations: {result.get('error', 'Unbekannt')}")
    print(f"   Leonardo: {result.get('error', 'Unbekannt')}")
    
    return {
        "success": False,
        "error": "Beide Bildgenerierungs-Dienste fehlgeschlagen"
    }

def main():
    parser = argparse.ArgumentParser(
        description="Bildgenerierung mit automatischem Fallback (Pollinations → Leonardo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Standard (Pollinations zuerst, dann Leonardo)
  python3 generate_with_fallback.py "Ein elegantes Maskottchen"
  
  # Eigene Auflösung
  python3 generate_with_fallback.py "Eine Katze" --width 768 --height 1024
  
  # Direkter Pfad
  python3 generate_with_fallback.py "Ein Hund" --output /tmp/meinhund.png
        """
    )
    
    parser.add_argument("prompt", help="Beschreibung des gewünschten Bildes")
    parser.add_argument("--width", "-W", type=int, default=1024,
                       choices=[512, 768, 1024], help="Bildbreite (default: 1024)")
    parser.add_argument("--height", "-H", type=int, default=1024,
                       choices=[512, 768, 1024], help="Bildhöhe (default: 1024)")
    parser.add_argument("--output", "-o", help="Ausgabepfad")
    parser.add_argument("--leonardo-model", "-m", default="flux-schnell",
                       choices=["flux-schnell", "flux-dev", "lucid-origin", "lucid-realism",
                               "anime-xl", "lightning-xl", "kino-xl", "vision-xl",
                               "rpg-v5", "dreamshaper-v7", "albedobase-xl"],
                       help="Leonardo Fallback-Modell (default: flux-schnell)")
    
    args = parser.parse_args()
    
    # Bild generieren
    result = generate_image_with_fallback(
        prompt=args.prompt,
        width=args.width,
        height=args.height,
        output_path=args.output,
        leonardo_model=args.leonardo_model
    )
    
    if result["success"]:
        print(f"\n🎉 Bild erfolgreich generiert!")
        print(f"   Anbieter: {result['provider']}")
        print(f"   Pfad: {result['path']}")
        if 'model' in result:
            print(f"   Modell: {result['model']}")
        sys.exit(0)
    else:
        print(f"\n❌ Fehler: {result.get('error', 'Unbekannt')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
