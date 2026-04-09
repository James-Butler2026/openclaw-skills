#!/usr/bin/env python3
"""
Kostenlose Bildgenerierung via Pollinations.ai API
Kein API-Key nötig, keine Rate-Limits bekannt
"""

import argparse
import urllib.parse
import urllib.request
import sys
from pathlib import Path


def generate_image(prompt: str, width: int = 512, height: int = 512, 
                   seed: int = 42, output: str = None, nologo: bool = True) -> str:
    """
    Generiert ein Bild via Pollinations.ai API
    
    Args:
        prompt: Bildbeschreibung/Prompt
        width: Bildbreite (default: 512)
        height: Bildhöhe (default: 512)
        seed: Seed für Reproduzierbarkeit (default: 42)
        output: Ausgabepfad (default: auto-generiert)
        nologo: Kein Watermark (default: True)
    
    Returns:
        Pfad zur generierten Bilddatei
    """
    # URL-encode den Prompt
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Baue die URL
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    params = []
    if width:
        params.append(f"width={width}")
    if height:
        params.append(f"height={height}")
    if seed is not None:
        params.append(f"seed={seed}")
    if nologo:
        params.append("nologo=true")
    
    if params:
        url += "?" + "&".join(params)
    
    # Bestimme Ausgabedatei
    if not output:
        safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip("_")
        output = f"/tmp/{safe_name}_seed{seed}.png"
    
    # Lade das Bild herunter
    print(f"🎨 Generiere Bild...")
    print(f"   Prompt: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    print(f"   Größe: {width}x{height}")
    print(f"   Seed: {seed}")
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            data = response.read()
            
        with open(output, "wb") as f:
            f.write(data)
        
        file_size = len(data) / 1024  # KB
        print(f"✅ Bild gespeichert: {output}")
        print(f"   Größe: {file_size:.1f} KB")
        
        return output
        
    except Exception as e:
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Kostenlose Bildgenerierung via Pollinations.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s "A beautiful sunset over mountains"
  %(prog)s "Digital art of a cyberpunk city" --width 1024 --height 768
  %(prog)s "Portrait of a cat" --seed 123 --output mycat.png
        """
    )
    
    parser.add_argument("prompt", help="Bildbeschreibung/Prompt (in Anführungszeichen)")
    parser.add_argument("--width", type=int, default=512, help="Bildbreite (default: 512)")
    parser.add_argument("--height", type=int, default=512, help="Bildhöhe (default: 512)")
    parser.add_argument("--seed", type=int, default=42, help="Seed für Reproduzierbarkeit (default: 42)")
    parser.add_argument("--output", "-o", help="Ausgabedatei (default: auto-generiert)")
    parser.add_argument("--logo", action="store_true", help="Watermarkerlaubnis (default: aus)")
    
    args = parser.parse_args()
    
    result = generate_image(
        prompt=args.prompt,
        width=args.width,
        height=args.height,
        seed=args.seed,
        output=args.output,
        nologo=not args.logo
    )
    
    print(result)  # Ausgabe für Piping/Scripting


if __name__ == "__main__":
    main()
