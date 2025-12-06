#!/usr/bin/env python3
"""Command-line interface for Learn in Sleep TTS."""

import argparse
import sys
from pathlib import Path

# Check Python version before importing TTS
if sys.version_info < (3, 10):
    print("ERROR: Python 3.10 or higher is required.")
    print(f"Current Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("\nPlease upgrade Python or use a virtual environment with Python 3.10+")
    print("Example:")
    print("  python3.10 -m venv .venv")
    print("  source .venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)

try:
    from learn_in_sleep_tts.tts_engine import synthesize_to_wav
    from learn_in_sleep_tts.utils import log_info, log_error
except ImportError as e:
    if "TTS" in str(e) or "bangla" in str(e):
        print("ERROR: Failed to import TTS library.")
        print("This is likely due to Python version incompatibility.")
        print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("\nCoqui TTS 0.22+ requires Python 3.10 or higher.")
        print("Please upgrade to Python 3.10+ or use an older TTS version.")
        sys.exit(1)
    raise


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Text-to-speech using Coqui TTS (XTTS v2 or VITS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Input options (mutually exclusive, required unless listing speakers)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--text",
        type=str,
        help="Text to synthesize (inline)",
    )
    input_group.add_argument(
        "--input-file",
        type=Path,
        help="Path to text file to synthesize",
    )
    
    # Output option (not required if just listing speakers)
    parser.add_argument(
        "--output",
        type=Path,
        required=False,
        help="Output WAV file path",
    )
    
    # Optional model override
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="TTS model name override (optional)",
    )
    
    # Optional speaker selection (for multi-speaker models like VCTK)
    parser.add_argument(
        "--speaker",
        type=str,
        default=None,
        help="Speaker ID (e.g., 'p225' for male storytelling voice, 'p226' for another male voice). Use --list-speakers to see available options.",
    )
    
    # List available speakers
    parser.add_argument(
        "--list-speakers",
        action="store_true",
        help="List available speakers for the selected model and exit",
    )
    
    args = parser.parse_args()
    
    # List speakers if requested (exit early)
    if args.list_speakers:
        try:
            from learn_in_sleep_tts.tts_engine import get_tts_model
            tts = get_tts_model(args.model)
            if hasattr(tts, 'speakers') and tts.speakers:
                print(f"\n📢 Available speakers ({len(tts.speakers)} total):")
                print("=" * 60)
                # Group by gender (p-prefixed are typically male)
                male_speakers = [s for s in tts.speakers if isinstance(s, str) and s.startswith('p')]
                female_speakers = [s for s in tts.speakers if isinstance(s, str) and not s.startswith('p') and s.strip()]
                
                if male_speakers:
                    print(f"\n👨 Male speakers ({len(male_speakers)}):")
                    for i, speaker in enumerate(male_speakers[:30], 1):  # Show first 30
                        marker = " ⭐" if speaker == "p225" else ""
                        print(f"   {speaker}{marker}")
                    if len(male_speakers) > 30:
                        print(f"   ... and {len(male_speakers) - 30} more")
                
                if female_speakers:
                    print(f"\n👩 Female speakers ({len(female_speakers)}):")
                    for speaker in female_speakers[:20]:  # Show first 20
                        print(f"   {speaker}")
                    if len(female_speakers) > 20:
                        print(f"   ... and {len(female_speakers) - 20} more")
                
                print(f"\n💡 Tip: p225 is recommended for male storytelling voice")
                print(f"   Use --speaker <speaker_id> to select a voice")
            else:
                print("⚠️  This model does not support speaker selection")
        except Exception as e:
            log_error(f"Error listing speakers: {e}")
            sys.exit(1)
        return
    
    # Validate required arguments for synthesis
    if not args.list_speakers:
        if not args.output:
            parser.error("--output is required when generating audio (use --list-speakers to see available voices)")
        if not args.text and not args.input_file:
            parser.error("Either --text or --input-file is required when generating audio")
    
    # Read text from the chosen source (skip if just listing speakers)
    if args.list_speakers:
        pass  # Already handled above
    elif args.text:
        text = args.text
    else:
        try:
            text = args.input_file.read_text(encoding="utf-8")
            log_info(f"Read {len(text)} characters from {args.input_file}")
        except Exception as e:
            log_error(f"Error reading input file: {e}")
            sys.exit(1)
    
    if not text.strip():
        log_error("Input text is empty")
        sys.exit(1)
    
    # Synthesize
    try:
        log_info(f"Generating audio for {len(text)} characters...")
        synthesize_to_wav(text, args.output, model_name=args.model, speaker_idx=args.speaker)
        log_info(f"✓ Success! Output saved to: {args.output}")
    except Exception as e:
        log_error(f"Error during synthesis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


