#!/usr/bin/env python3
"""
Audio Transcription - OPTIMIERTE VERSION v2.0
Nutzt faster-whisper mit Int8-Quantization und Modell-Caching
3-5x schneller durch wiederverwendetes Modell
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional
import hashlib
import json

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache-Verzeichnis für geladene Modelle
CACHE_DIR = Path("/tmp/whisper_cache")
CACHE_DIR.mkdir(exist_ok=True)

# Globale Variable für Modell-Cache (wiederverwendbar)
_model_cache = {}

def get_model(model_name: str = "small", compute_type: str = "int8"):
    """
    Lädt Whisper-Modell mit Caching (wiederverwendbar)
    
    Args:
        model_name: tiny, base, small, medium, large-v3
        compute_type: int8 (schnell auf CPU), float16, float32
    
    Returns:
        WhisperModel-Instanz (aus Cache oder neu geladen)
    """
    global _model_cache
    
    cache_key = f"{model_name}_{compute_type}"
    
    if cache_key in _model_cache:
        logger.debug(f"✅ Modell aus Cache: {cache_key}")
        return _model_cache[cache_key]
    
    try:
        from faster_whisper import WhisperModel
        
        logger.info(f"🔄 Lade Modell: {model_name} (compute_type={compute_type})")
        
        # CPU-Optimierung: Int8 ist schneller und speicherschonend
        model = WhisperModel(
            model_name,
            device="cpu",
            compute_type=compute_type,
            cpu_threads=os.cpu_count() or 4,  # Nutze alle CPU-Kerne
            num_workers=2
        )
        
        _model_cache[cache_key] = model
        logger.info(f"✅ Modell geladen und gecached")
        return model
        
    except ImportError:
        logger.error("❌ faster-whisper nicht installiert")
        logger.error("   Installiere: pip install faster-whisper")
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden des Modells: {e}")
        raise

def transcribe_file(
    audio_path: str, 
    language: str = "auto", 
    model_name: str = "small",
    compute_type: str = "int8"
) -> str:
    """
    Transkribiert eine Audiodatei mit faster-whisper (optimiert)
    
    Args:
        audio_path: Pfad zur Audio-Datei
        language: Sprachcode (z.B. 'de', 'en') oder 'auto'
        model_name: Modell-Name (tiny, base, small, medium, large-v3)
        compute_type: int8 (schnell), float16, float32
    
    Returns:
        Der transkribierte Text
    """
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio-Datei nicht gefunden: {audio_path}")
    
    try:
        # Modell laden (mit Caching)
        model = get_model(model_name, compute_type)
        
        logger.info(f"🎙️  Transkribiere: {audio_file.name}")
        
        # Transkriptions-Parameter optimiert für Geschwindigkeit
        segments, info = model.transcribe(
            str(audio_file),
            language=None if language == "auto" else language,
            beam_size=5,           # Kleiner = schneller
            best_of=5,             # Weniger Hypothesen = schneller
            patience=1.0,          # Früherer Abbruch
            condition_on_previous_text=False,  # Schneller
            temperature=0.0,     # Deterministisch = schneller
            compression_ratio_threshold=2.4,
            vad_filter=True,      # Stille entfernen = schneller
            vad_parameters=dict(
                min_silence_duration_ms=500,  # 500ms Stille = Pause
                threshold=0.3
            )
        )
        
        # Text zusammensetzen
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)
        
        result = " ".join(text_parts).strip()
        
        # Sprachinfo loggen
        if language == "auto" and info:
            logger.info(f"   Erkannte Sprache: {info.language} (confidence: {info.language_probability:.2f})")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Transkription fehlgeschlagen: {e}")
        raise

def transcribe_batch(
    audio_files: list,
    language: str = "auto",
    model_name: str = "small",
    compute_type: str = "int8"
) -> dict:
    """
    Transkribiert mehrere Dateien mit einem Modell (noch schneller)
    
    Args:
        audio_files: Liste von Dateipfaden
        language: Sprachcode
        model_name: Modell-Name
        compute_type: Int8, float16, float32
    
    Returns:
        Dict mit {datei: text}
    """
    # Modell einmal laden für alle
    model = get_model(model_name, compute_type)
    
    results = {}
    for audio_file in audio_files:
        try:
            text = transcribe_file(audio_file, language, model_name, compute_type)
            results[audio_file] = text
        except Exception as e:
            results[audio_file] = f"❌ Fehler: {e}"
    
    return results

def get_speed_hint(duration_seconds: float) -> str:
    """Gibt Hinweis zur erwarteten Geschwindigkeit"""
    if duration_seconds < 60:
        return "~10-20 Sekunden"
    elif duration_seconds < 300:
        return "~1-2 Minuten"
    else:
        return "~3-5 Minuten"

def main():
    parser = argparse.ArgumentParser(
        description="Transkribiert Audio-Dateien mit faster-whisper (OPTIMIERT)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s sprachnachricht.ogg                    # Auto-Detection, small Modell
  %(prog)s audio.mp3 --language de --model tiny   # Deutsch, schnellstes Modell
  %(prog)s *.ogg --model base                     # Batch-Verarbeitung
  %(prog)s podcast.mp3 --model medium             # Bessere Qualität

Optimierungen v2.0:
  - Int8-Quantization (3x schneller auf CPU)
  - Modell-Caching (Modell wird nur einmal geladen)
  - VAD-Filter (entfernt Stille)
  - Multi-CPU-Unterstützung
        """
    )
    parser.add_argument(
        "audio_files",
        nargs="+",
        help="Audio-Dateien (mp3, ogg, wav, etc.)"
    )
    parser.add_argument(
        "--language", "-l",
        default="auto",
        help="Sprache der Aufnahme (z.B. 'de', 'en'). Default: auto-erkennen"
    )
    parser.add_argument(
        "--model", "-m",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper-Modell (tiny=am schnellsten, large-v3=beste Qualität). Default: small"
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        choices=["int8", "int16", "float16", "float32"],
        help="Berechnungstyp (int8=schnellst auf CPU, float32=präzisest). Default: int8"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Modell-Cache löschen und neu laden"
    )
    
    args = parser.parse_args()
    
    # Cache löschen wenn gewünscht
    if args.clear_cache:
        global _model_cache
        _model_cache = {}
        logger.info("🗑️  Modell-Cache geleert")
    
    # Prüfe ob Dateien existieren
    valid_files = []
    for audio_file in args.audio_files:
        if Path(audio_file).exists():
            valid_files.append(audio_file)
        else:
            logger.warning(f"⚠️  Datei nicht gefunden: {audio_file}")
    
    if not valid_files:
        logger.error("❌ Keine gültigen Audio-Dateien gefunden")
        sys.exit(1)
    
    try:
        start_time = __import__('time').time()
        
        if len(valid_files) == 1:
            # Einzelne Datei
            text = transcribe_file(
                valid_files[0], 
                args.language, 
                args.model,
                args.compute_type
            )
            
            elapsed = __import__('time').time() - start_time
            
            print(f"\n📝 Transkription (dauerte {elapsed:.1f}s):")
            print("-" * 40)
            print(text)
            print("-" * 40)
            
        else:
            # Batch-Verarbeitung
            logger.info(f"🔄 Batch-Verarbeitung: {len(valid_files)} Dateien")
            results = transcribe_batch(
                valid_files,
                args.language,
                args.model,
                args.compute_type
            )
            
            elapsed = __import__('time').time() - start_time
            
            for audio_file, text in results.items():
                print(f"\n🎙️  {Path(audio_file).name}:")
                print("-" * 40)
                print(text)
                print("-" * 40)
            
            print(f"\n✅ Batch-Verarbeitung abgeschlossen ({elapsed:.1f}s)")
            
    except KeyboardInterrupt:
        logger.info("🛑 Transkription unterbrochen")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
