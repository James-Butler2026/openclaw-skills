#!/usr/bin/env python3
"""
Audio Transcription v2.1 - ÜBERARBEITET
Nutzt faster-whisper mit Int8-Quantization, Zeitstempeln, Output-Datei und Fortschrittsanzeige
"""

import argparse
import sys
import os
import logging
import time
import json
from pathlib import Path
from typing import Optional, Dict, List
import tempfile

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Globale Variable für Modell-Cache
_model_cache = {}

# Valide Audio-Formate
VALID_AUDIO_EXTENSIONS = {'.mp3', '.ogg', '.wav', '.m4a', '.flac', '.aac', '.wma'}


def validate_audio_file(audio_path: str) -> bool:
    """Prüft ob Datei ein gültiges Audio-Format hat"""
    ext = Path(audio_path).suffix.lower()
    if ext not in VALID_AUDIO_EXTENSIONS:
        logger.warning(f"⚠️  Unbekanntes Format: {ext}. Unterstützt: {', '.join(VALID_AUDIO_EXTENSIONS)}")
        return False
    return True


def get_audio_duration(audio_path: str) -> float:
    """Versucht die Länge der Audio-Datei zu ermitteln"""
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass
    return 0.0


def get_speed_hint(duration_seconds: float) -> str:
    """Gibt Hinweis zur erwarteten Geschwindigkeit"""
    if duration_seconds == 0:
        return "Unbekannt"
    elif duration_seconds < 60:
        return "~10-20 Sekunden"
    elif duration_seconds < 300:
        return "~1-2 Minuten"
    elif duration_seconds < 900:
        return "~2-5 Minuten"
    else:
        return "~5-15 Minuten"


def format_timestamp(seconds: float) -> str:
    """Formatiert Sekunden zu [HH:MM:SS] oder [MM:SS]"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"


def get_model(model_name: str = "medium", compute_type: str = "int8"):
    """Lädt Whisper-Modell mit Caching"""
    global _model_cache
    
    cache_key = f"{model_name}_{compute_type}"
    
    if cache_key in _model_cache:
        logger.debug(f"✅ Modell aus Cache: {cache_key}")
        return _model_cache[cache_key]
    
    try:
        from faster_whisper import WhisperModel
        
        logger.info(f"🔄 Lade Modell: {model_name} (compute_type={compute_type})")
        
        model = WhisperModel(
            model_name,
            device="cpu",
            compute_type=compute_type,
            cpu_threads=os.cpu_count() or 4,
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
    model_name: str = "medium",
    compute_type: str = "int8",
    timestamps: bool = False,
    progress: bool = True
) -> Dict:
    """
    Transkribiert eine Audiodatei mit Zeitstempeln und Konfidenz
    
    Returns:
        Dict mit {'text': str, 'segments': [{'start', 'end', 'text', 'confidence'}]}
    """
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio-Datei nicht gefunden: {audio_path}")
    
    if not validate_audio_file(audio_path):
        raise ValueError(f"Ungültiges Audio-Format: {audio_path}")
    
    try:
        model = get_model(model_name, compute_type)
        
        logger.info(f"🎙️  Transkribiere: {audio_file.name}")
        
        # Audio-Länge für Fortschrittsanzeige
        duration = get_audio_duration(audio_path)
        if duration > 0:
            logger.info(f"   Dauer: {duration:.0f}s | Geschätzte Zeit: {get_speed_hint(duration)}")
        
        start_time = time.time()
        
        segments, info = model.transcribe(
            str(audio_file),
            language=None if language == "auto" else language,
            beam_size=5,
            best_of=5,
            patience=1.0,
            condition_on_previous_text=False,
            temperature=0.0,
            compression_ratio_threshold=2.4,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                threshold=0.3
            )
        )
        
        # Segmente verarbeiten
        result_segments = []
        text_parts = []
        last_progress = 0
        
        for i, segment in enumerate(segments):
            segment_data = {
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'confidence': getattr(segment, 'avg_logprob', 0.0)
            }
            result_segments.append(segment_data)
            text_parts.append(segment.text.strip())
            
            # Fortschrittsanzeige
            if progress and duration > 0:
                progress_pct = min(int((segment.end / duration) * 100), 100)
                if progress_pct > last_progress + 10:
                    elapsed = time.time() - start_time
                    eta = (elapsed / progress_pct * 100) - elapsed if progress_pct > 0 else 0
                    logger.info(f"   Fortschritt: {progress_pct}% | ETA: {eta:.0f}s")
                    last_progress = progress_pct
        
        elapsed = time.time() - start_time
        result_text = " ".join(text_parts).strip()
        
        # Sprachinfo
        if language == "auto" and info:
            logger.info(f"   Erkannte Sprache: {info.language} (confidence: {info.language_probability:.2f})")
        
        logger.info(f"   ✅ Fertig in {elapsed:.1f}s")
        
        return {
            'text': result_text,
            'segments': result_segments,
            'language': info.language if info else 'unknown',
            'duration': duration,
            'processing_time': elapsed
        }
        
    except Exception as e:
        logger.error(f"❌ Transkription fehlgeschlagen: {e}")
        raise


def save_transcription(result: Dict, output_path: str, timestamps: bool = False, confidence: bool = False):
    """Speichert Transkription in Datei"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    lines.append(f"# Transkription\n")
    lines.append(f"Sprache: {result['language']}\n")
    lines.append(f"Dauer: {result['duration']:.0f}s | Verarbeitung: {result['processing_time']:.1f}s\n")
    lines.append("=" * 50 + "\n\n")
    
    if timestamps:
        # Mit Zeitstempeln und optional Konfidenz
        for seg in result['segments']:
            ts = format_timestamp(seg['start'])
            conf_str = f" (confidence: {seg['confidence']:.2f})" if confidence else ""
            lines.append(f"{ts} {seg['text']}{conf_str}\n")
    else:
        # Nur Text
        lines.append(result['text'] + "\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    logger.info(f"💾 Gespeichert: {output_file}")
    return output_file


def transcribe_batch(
    audio_files: List[str],
    language: str = "auto",
    model_name: str = "medium",
    compute_type: str = "int8",
    timestamps: bool = False,
    confidence: bool = False,
    output_dir: Optional[str] = None,
    progress: bool = True
) -> Dict[str, Dict]:
    """Transkribiert mehrere Dateien"""
    model = get_model(model_name, compute_type)
    
    results = {}
    for i, audio_file in enumerate(audio_files, 1):
        logger.info(f"\n🎙️  [{i}/{len(audio_files)}] {Path(audio_file).name}")
        try:
            result = transcribe_file(audio_file, language, model_name, compute_type, timestamps, progress)
            results[audio_file] = result
            
            # Auto-Output wenn Verzeichnis angegeben
            if output_dir:
                output_name = Path(audio_file).stem + "_transcript.txt"
                output_path = Path(output_dir) / output_name
                save_transcription(result, str(output_path), timestamps, confidence)
                
        except Exception as e:
            logger.error(f"❌ Fehler bei {audio_file}: {e}")
            results[audio_file] = {'text': f'Fehler: {e}', 'segments': [], 'error': str(e)}
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Audio Transcription v2.1 - Mit Zeitstempeln, Output-Datei und Fortschrittsanzeige",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s sprachnachricht.ogg                          # Standard (medium, int8)
  %(prog)s audio.mp3 --language de --output text.txt     # Deutsch + speichern
  %(prog)s podcast.mp3 --timestamps --output out.txt    # Mit Zeitstempeln
  %(prog)s *.ogg --output-dir ./transcripts/             # Batch + Auto-Speichern
  %(prog)s interview.wav --model large-v3 --confidence  # Beste Qualität + Konfidenz

Modelle (schnell → präzise):
  tiny < base < small < medium < large-v3

Neu in v2.1:
  - Zeitstempel-Option
  - Output-Datei
  - Fortschrittsanzeige
  - Konfidenz-Scores
  - Audio-Format-Validierung
        """
    )
    parser.add_argument(
        "audio_files",
        nargs="+",
        help="Audio-Dateien (mp3, ogg, wav, m4a, flac, aac)"
    )
    parser.add_argument(
        "--language", "-l",
        default="auto",
        help="Sprache (z.B. 'de', 'en'). Default: auto-erkennen"
    )
    parser.add_argument(
        "--model", "-m",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper-Modell. Default: medium"
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        choices=["int8", "int16", "float16", "float32"],
        help="Berechnungstyp. Default: int8"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output-Datei (bei einer Datei)"
    )
    parser.add_argument(
        "--output-dir",
        help="Output-Verzeichnis (bei mehreren Dateien)"
    )
    parser.add_argument(
        "--timestamps", "-t",
        action="store_true",
        help="Zeitstempel für jedes Segment hinzufügen"
    )
    parser.add_argument(
        "--confidence", "-c",
        action="store_true",
        help="Konfidenz-Scores anzeigen"
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Fortschrittsanzeige deaktivieren"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Modell-Cache löschen"
    )
    
    args = parser.parse_args()
    
    # Cache löschen
    if args.clear_cache:
        global _model_cache
        _model_cache = {}
        logger.info("🗑️  Modell-Cache geleert")
    
    # Dateien validieren
    valid_files = []
    for audio_file in args.audio_files:
        if Path(audio_file).exists():
            if validate_audio_file(audio_file):
                valid_files.append(audio_file)
        else:
            logger.warning(f"⚠️  Datei nicht gefunden: {audio_file}")
    
    if not valid_files:
        logger.error("❌ Keine gültigen Audio-Dateien gefunden")
        sys.exit(1)
    
    try:
        progress = not args.no_progress
        
        if len(valid_files) == 1:
            # Einzelne Datei
            result = transcribe_file(
                valid_files[0], 
                args.language, 
                args.model,
                args.compute_type,
                args.timestamps,
                progress
            )
            
            # Output
            if args.output:
                save_transcription(result, args.output, args.timestamps, args.confidence)
            
            # Console-Output
            print(f"\n📝 Transkription:")
            print("-" * 50)
            if args.timestamps:
                for seg in result['segments']:
                    ts = format_timestamp(seg['start'])
                    conf_str = f" (confidence: {seg['confidence']:.2f})" if args.confidence else ""
                    print(f"{ts} {seg['text']}{conf_str}")
            else:
                print(result['text'])
            print("-" * 50)
            print(f"\n   Sprache: {result['language']}")
            print(f"   Dauer: {result['duration']:.0f}s")
            print(f"   Verarbeitung: {result['processing_time']:.1f}s")
            
        else:
            # Batch
            logger.info(f"🔄 Batch-Verarbeitung: {len(valid_files)} Dateien")
            results = transcribe_batch(
                valid_files,
                args.language,
                args.model,
                args.compute_type,
                args.timestamps,
                args.confidence,
                args.output_dir,
                progress
            )
            
            print(f"\n✅ Batch abgeschlossen: {len(results)} Dateien")
            
    except KeyboardInterrupt:
        logger.info("🛑 Transkription unterbrochen")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
