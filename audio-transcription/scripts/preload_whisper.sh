#!/bin/bash
# Faster-Whisper Preload - Lädt Modell beim Gateway-Start
# Hält das Modell dauerhaft im RAM

VENV_PYTHON="/home/node/.openclaw/venv/bin/python3"
SCRIPT_DIR="/home/node/.openclaw/workspace/skills/audio-transcription/scripts"
PID_FILE="/tmp/faster_whisper_preload.pid"
LOG_FILE="/tmp/faster_whisper_preload.log"

# Nur starten wenn nicht schon aktiv
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "✅ Faster-Whisper bereits geladen (PID: $(cat $PID_FILE))"
    exit 0
fi

echo "🔄 Lade Faster-Whisper Modell (medium, int8) in RAM..."

# Python-Script das Modell lädt und hält
cat > /tmp/preload_whisper.py << 'PYEOF'
#!/usr/bin/env python3
"""Lädt Whisper-Modell und hält es permanent im RAM"""
import os
import sys
import signal
import time
import logging

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/faster_whisper_preload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Globale Variable für Modell - verhindert Garbage Collection
_model = None

def load_model():
    """Lädt das Whisper-Modell und hält es im RAM"""
    global _model
    
    logger.info("🔄 Lade Whisper Medium Modell (int8)...")
    start = time.time()
    
    try:
        from faster_whisper import WhisperModel
        
        # Modell laden -medium, int8, CPU
        _model = WhisperModel(
            "medium",
            device="cpu",
            compute_type="int8",
            cpu_threads=os.cpu_count() or 4,
            num_workers=2
        )
        
        elapsed = time.time() - start
        logger.info(f"✅ Modell geladen in {elapsed:.1f}s - jetzt im RAM (Vermeide Neuladen)")
        logger.info(f"📊 Modell-Größe: ~1.5GB RAM")
        logger.info("🟢 Halte Modell permanent im RAM...")
        
        # Modell bleibt geladen - endloss loop
        while True:
            time.sleep(3600)  # 1 Stunde schlafen, dann wieder schlafen
            
    except ImportError:
        logger.error("❌ faster-whisper nicht installiert!")
        logger.error("   Installiere: /home/node/.openclaw/venv/bin/pip install faster-whisper")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        sys.exit(1)

def signal_handler(sig, frame):
    logger.info("🛑 Beende Whisper Preload...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    load_model()
PYEOF

# Starte Preload im Hintergrund
nohup $VENV_PYTHON /tmp/preload_whisper.py > /tmp/faster_whisper_preload.out.log 2>&1 &
PRELOAD_PID=$!

# PID speichern
echo $PRELOAD_PID > "$PID_FILE"

# Kurze Zeit warten und prüfen ob Prozess läuft
sleep 2
if kill -0 $PRELOAD_PID 2>/dev/null; then
    echo "✅ Faster-Whisper Preload gestartet (PID: $PRELOAD_PID)"
    echo "📝 Log: $LOG_FILE"
    exit 0
else
    echo "❌ Preload fehlgeschlagen - prüfe Log"
    cat /tmp/faster_whisper_preload.out.log
    exit 1
fi
