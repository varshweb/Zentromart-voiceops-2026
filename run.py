#!/usr/bin/env python3
"""VoiceOps 2026 Batch Runner.

Usage:
    python3 run.py --input-dir /path/to/customer_audio --output-dir /path/to/output

Processes a folder of customer audio files:
1. Transcribes incoming audio via Gnani STT.
2. Runs the multi-turn conversational agent with RAG & Mock Tools.
3. Synthesizes voice response via Gnani TTS into an output WAV file.
4. Saves a structured JSON log containing replies, decisions, tool calls, and retrieved document chunks.
"""

import os
import sys
import argparse
import json
import glob
import importlib.util

_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_load("retriever", os.path.join(_SRC, "retriever.py"))
_load("agent", os.path.join(_SRC, "agent.py"))
_load("voice", os.path.join(_SRC, "voice.py"))

from retriever import KBRetriever
from agent import SupportAgent
from voice import VoicePipeline


def parse_args():
    parser = argparse.ArgumentParser(description="VoiceOps 2026 Customer Support Voice Batch Runner")
    parser.add_argument("--input-dir", "-i", type=str, default="sample_audio",
                        help="Path to folder containing customer audio files (.wav, .mp3, etc.)")
    parser.add_argument("--output-dir", "-o", type=str, default="sample_outputs/batch_run",
                        help="Path to directory where output audio, transcripts, and logs will be saved")
    parser.add_argument("--kb-dir", type=str, default=None,
                        help="Path to knowledge base markdown files (default: auto-detected)")
    parser.add_argument("--data-dir", type=str, default=None,
                        help="Path to CSV data directory (default: auto-detected)")
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Locate KB and Data directories
    kb_dir = args.kb_dir
    if not kb_dir:
        for candidate in [os.path.join(_ROOT, "kb"), os.path.join(_ROOT, "Capstone_Project_Dataset_FTTT_2026", "kb")]:
            if os.path.exists(candidate):
                kb_dir = candidate
                break
                
    data_dir = args.data_dir
    if not data_dir:
        for candidate in [os.path.join(_ROOT, "data"), os.path.join(_ROOT, "Capstone_Project_Dataset_FTTT_2026", "data")]:
            if os.path.exists(candidate):
                data_dir = candidate
                break

    prod_path = os.path.join(data_dir, "products.csv") if data_dir else None

    print(f"Initializing ZentroMart VoiceOps Agent...")
    print(f"  - Knowledge Base: {kb_dir}")
    print(f"  - Data Directory: {data_dir}")
    print(f"  - Input Audio Dir: {args.input_dir}")
    print(f"  - Output Dir:     {args.output_dir}")

    retriever = KBRetriever(kb_dir=kb_dir, products_csv_path=prod_path)
    agent = SupportAgent(retriever=retriever)
    voice = VoicePipeline()

    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all audio files in input-dir
    audio_files = []
    if os.path.exists(args.input_dir):
        for ext in ["*.wav", "*.mp3", "*.ogg", "*.flac"]:
            audio_files.extend(sorted(glob.glob(os.path.join(args.input_dir, ext))))

    if not audio_files:
        print(f"No audio files found in {args.input_dir}. (Create sample .wav files to test batch runner).")
        # Generate a demonstration test turn
        dummy_audio = os.path.join(args.input_dir, "demo_call_01.wav")
        os.makedirs(args.input_dir, exist_ok=True)
        # Create companion text for offline demonstration
        dummy_txt = os.path.join(args.input_dir, "demo_call_01.txt")
        with open(dummy_txt, "w", encoding="utf-8") as f:
            f.write("Hello, I need help with my order.")
        voice.synthesize("Test customer speech", dummy_audio)
        audio_files = [dummy_audio]

    results = []
    for idx, audio_path in enumerate(audio_files, 1):
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_wav = os.path.join(args.output_dir, f"{base_name}_reply.wav")
        
        print(f"[{idx}/{len(audio_files)}] Processing: {os.path.basename(audio_path)}...")
        
        turn_result = voice.process_voice_turn(
            audio_path=audio_path,
            agent=agent,
            output_wav_path=output_wav
        )
        
        # Retrieve chunks used for grounding
        chunks = retriever.search(turn_result["transcript"], top_k=3)
        retrieved_ids = [c["sec_id"] for c in chunks]
        
        turn_result["retrieved_chunks"] = retrieved_ids
        turn_result["audio_file"] = os.path.basename(audio_path)
        turn_result["reply_audio_file"] = os.path.basename(output_wav)
        
        results.append(turn_result)
        print(f"  Transcript: {turn_result['transcript']}")
        print(f"  Decision  : {turn_result['decision']}")
        print(f"  Reply Text: {turn_result['reply_text']}")
        print(f"  Citations : {retrieved_ids}")
        print(f"  Saved WAV : {output_wav}\n")

    summary_file = os.path.join(args.output_dir, "run_results.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({"total_processed": len(results), "turns": results}, f, indent=2, ensure_ascii=False)

    print(f"Batch processing completed successfully! Summary log saved to: {summary_file}")


if __name__ == "__main__":
    main()
