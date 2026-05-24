#!/usr/bin/env python3
"""MusicGen Generator via HuggingFace Transformers (kein audiocraft nötig!)
Usage: python3 generate.py --prompt "rock guitar riff" --output song.wav --duration 8
"""
import sys, os, json, argparse, time, warnings
warnings.filterwarnings("ignore")

def main():
    parser = argparse.ArgumentParser(description="MusicGen Generator")
    parser.add_argument("--prompt", default="rock guitar riff")
    parser.add_argument("--output", default="output.wav")
    parser.add_argument("--duration", type=int, default=8)
    args = parser.parse_args()

    try:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        import soundfile as sf
    except ImportError as e:
        print(json.dumps({"error": f"Fehlende Abhängigkeit: {e}"}))
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_id = "facebook/musicgen-small"

    print(f"🎵 Lade MusicGen (small) auf {device} ...", file=sys.stderr)
    t0 = time.time()
    
    processor = AutoProcessor.from_pretrained(model_id)
    model = MusicgenForConditionalGeneration.from_pretrained(model_id)
    model = model.to(device)
    
    print(f"   ✅ Geladen in {time.time()-t0:.1f}s", file=sys.stderr)

    inputs = processor(
        text=[args.prompt],
        padding=True,
        return_tensors="pt",
    ).to(device)

    print(f"   🎶 Generiere Musik zu: '{args.prompt}' ~{args.duration}s ...", file=sys.stderr)
    t1 = time.time()
    
    audio_values = model.generate(**inputs, max_new_tokens=args.duration * 50)
    gen_time = time.time() - t1
    
    print(f"   ✅ Generiert in {gen_time:.1f}s", file=sys.stderr)

    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    
    sampling_rate = model.config.audio_encoder.sampling_rate
    sf.write(out_path, audio_values[0].cpu().numpy().T, sampling_rate)
    
    result = {
        "status": "ok",
        "output": out_path,
        "duration_s": args.duration,
        "gen_time_s": round(gen_time, 1),
        "prompt": args.prompt,
        "model": model_id
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
