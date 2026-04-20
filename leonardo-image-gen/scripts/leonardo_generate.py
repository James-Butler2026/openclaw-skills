#!/usr/bin/env python3
"""
Leonardo AI Image Generator
Bildgenerierung via Leonardo AI API
"""

import os
import sys
import argparse
import time
import base64
from pathlib import Path
import requests
from dotenv import load_dotenv

# Lade .env Datei
load_dotenv("/home/node/.openclaw/workspace/.env")

# Farben für Output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"{Colors.HEADER}{Colors.BOLD}🎨 {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

class LeonardoAI:
    """Leonardo AI API Client"""
    
    BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
    
    # Bekannte Modelle
    MODELS = {
        # FLUX Modelle (empfohlen)
        "flux-schnell": "1dd50843-d653-4516-a8e3-f0238ee453ff",
        "flux-dev": "b2614463-296c-462a-9586-aafdb8f00e36",
        
        # Lucid Modelle (sehr gute Qualität)
        "lucid-origin": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9",
        "lucid-realism": "05ce0082-2d80-4a2d-8653-4d1c85e2418e",
        
        # Leonardo XL Modelle
        "anime-xl": "e71a1c2f-4f80-4800-934f-2c68979d8cc8",
        "lightning-xl": "b24e16ff-06e3-43eb-8d33-4416c2d75876",
        "kino-xl": "aa77f04e-3eec-4034-9c07-d0f619684628",
        "vision-xl": "5c232a9e-9061-4777-980a-ddc8e65647c6",
        
        # Spezialisierte Modelle
        "rpg-v5": "f1929ea3-b169-4c18-a16c-5d58b4292c69",
        "dreamshaper-v7": "ac614f96-1082-45bf-be9d-757f2d31c17",
        "albedobase-xl": "2067ae52-33fd-4a82-bb92-c2c55e7d2786",
        
        # Legacy (für Kompatibilität)
        "diffusion-xl": "1e60896f-3c73-4721-9c1e-3f46f8024d20",
        "dreamshaper": "ac614f96-1082-45bf-be9d-757f2b2f8f84",
        "absolute-reality": "7c8a9f8a-6f3d-4b7e-8c2d-9e5f6a4b3c2d",
    }
    
    def __init__(self, api_key=None):
        """Initialisiere mit API Key"""
        self.api_key = api_key or os.getenv("LEONARDO_API_KEY")
        if not self.api_key:
            raise ValueError("API Key benötigt! Setze LEONARDO_API_KEY Umgebungsvariable.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def list_models(self):
        """Zeigt verfügbare Modelle an"""
        print_info("Verfügbare Modelle:")
        for name, model_id in self.MODELS.items():
            print(f"  - {name}: {model_id}")
        print_info("\nVerwende: --model MODEL_NAME")
        return self.MODELS
    
    def get_user_info(self):
        """Zeigt User-Infos (Credits, etc.)"""
        url = f"{self.BASE_URL}/me"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def generate_image(self, prompt, model_id=None, width=1024, height=1024, num_images=1):
        """
        Generiert ein Bild
        
        Args:
            prompt: Text-Beschreibung
            model_id: Leonardo Modell ID (optional)
            width: Bildbreite (512, 768, 1024)
            height: Bildhöhe (512, 768, 1024)
            num_images: Anzahl Bilder (1-8)
        """
        url = f"{self.BASE_URL}/generations"
        
        payload = {
            "prompt": prompt,
            "modelId": model_id,
            "width": width,
            "height": height,
            "num_images": num_images
        }
        
        print_info("Sende Anfrage an Leonardo AI...")
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            print_error(f"API Fehler: {response.status_code}")
            print_info(f"Antwort: {response.text[:200]}")
            return None
        
        data = response.json()
        generation_id = data.get("sdGenerationJob", {}).get("generationId")
        
        if not generation_id:
            print_error("Keine Generation ID erhalten")
            return None
        
        print_info(f"Generation ID: {generation_id}")
        print_info("Warte auf Bild... (kann 10-30 Sekunden dauern)")
        
        # Warte auf Fertigstellung
        return self.wait_for_image(generation_id)
    
    def wait_for_image(self, generation_id, max_attempts=30):
        """Wartet bis das Bild fertig ist"""
        url = f"{self.BASE_URL}/generations/{generation_id}"
        
        for attempt in range(max_attempts):
            time.sleep(2)  # Alle 2 Sekunden prüfen
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                continue
            
            data = response.json()
            generations = data.get("generations_by_pk", {}).get("generated_images", [])
            
            if generations:
                print_success(f"Bild fertig nach {attempt * 2} Sekunden!")
                return generations
            
            print(f"  Warte... ({attempt + 1}/{max_attempts})", end='\r')
        
        print_error("Timeout - Bild nicht fertiggestellt")
        return None
    
    def download_image(self, image_url, output_path):
        """Lädt Bild herunter"""
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path

def main():
    parser = argparse.ArgumentParser(
        description="Leonardo AI Bildgenerator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Mit API Key direkt
  python3 leonardo_generate.py "Ein elegantes Maskottchen" --key DEIN_KEY
  
  # Mit Umgebungsvariable
  export LEONARDO_API_KEY="dein_key"
  python3 leonardo_generate.py "Ein Roboter"
  
  # Eigene Auflösung
  python3 leonardo_generate.py "Eine Katze" --width 768 --height 768
  
  # Mehrere Bilder
  python3 leonardo_generate.py "Ein Hund" --num 4
        """
    )
    
    parser.add_argument("prompt", nargs="?", help="Beschreibung des gewünschten Bildes")
    parser.add_argument("--key", "-k", help="Leonardo AI API Key")
    parser.add_argument("--width", "-W", type=int, default=1024, 
                       choices=[512, 768, 1024], help="Bildbreite (default: 1024)")
    parser.add_argument("--height", "-H", type=int, default=1024,
                       choices=[512, 768, 1024], help="Bildhöhe (default: 1024)")
    parser.add_argument("--num", "-n", type=int, default=1,
                       help="Anzahl Bilder (1-8, default: 1)")
    parser.add_argument("--model", "-m", default="vision-xl", 
                       choices=["flux-schnell", "flux-dev", "lucid-origin", "lucid-realism",
                               "anime-xl", "lightning-xl", "kino-xl", "vision-xl",
                               "rpg-v5", "dreamshaper-v7", "albedobase-xl",
                               "diffusion-xl", "dreamshaper", "absolute-reality"],
                       help="Zu verwendendes Modell (default: vision-xl)")
    parser.add_argument("--output", "-o", help="Ausgabepfad")
    parser.add_argument("--info", action="store_true", help="Zeigt Account-Info (Credits)")
    parser.add_argument("--list-models", action="store_true", help="Zeigt alle verfügbaren Modelle")
    
    args = parser.parse_args()
    
    # API Key holen
    api_key = args.key or os.getenv("LEONARDO_API_KEY")
    
    if not api_key:
        print_error("Kein API Key angegeben!")
        print_info("So bekommst du einen Key:")
        print("  1. Gehe zu: https://leonardo.ai/")
        print("  2. Erstelle Account")
        print("  3. Settings → API Keys → Generate")
        print("  4. Verwende: --key DEIN_KEY oder setze LEONARDO_API_KEY")
        sys.exit(1)
    
    try:
        client = LeonardoAI(api_key)
        
        # Nur Info anzeigen
        if args.info:
            print_header("Account Information")
            info = client.get_user_info()
            print(info)
            return
        
        if not args.prompt:
            print_error("Bitte gib einen Prompt an oder verwende --info")
            parser.print_help()
            sys.exit(1)
        
        # Bild generieren
        print_header(f"Leonardo AI: {args.prompt[:50]}...")
        print_info(f"Auflösung: {args.width}x{args.height}")
        print_info(f"Anzahl: {args.num}")
        print()
        
        # Modell ID holen
        model_id = client.MODELS.get(args.model, client.MODELS["vision-xl"])
        print_info(f"Modell: {args.model}")
        
        start_time = time.time()
        images = client.generate_image(
            prompt=args.prompt,
            model_id=model_id,
            width=args.width,
            height=args.height,
            num_images=args.num
        )
        
        if not images:
            print_error("Bildgenerierung fehlgeschlagen!")
            sys.exit(1)
        
        # Bilder speichern
        output_dir = Path("/home/node/.openclaw/workspace/output/leonardo")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for i, img_data in enumerate(images):
            img_url = img_data.get("url")
            if img_url:
                if args.output and args.num == 1:
                    filename = Path(args.output)
                else:
                    timestamp = int(time.time())
                    filename = output_dir / f"leonardo_{timestamp}_{i+1}.png"
                
                client.download_image(img_url, filename)
                saved_files.append(filename)
                print_success(f"Gespeichert: {filename}")
        
        elapsed = time.time() - start_time
        print()
        print_header("Zusammenfassung")
        print_info(f"Generiert: {len(saved_files)} Bilder")
        print_info(f"Dauer: {elapsed:.1f} Sekunden")
        print_info(f"Ort: {output_dir}")
        
    except Exception as e:
        print_error(f"Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
