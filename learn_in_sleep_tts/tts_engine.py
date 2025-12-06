"""TTS engine using Coqui TTS for text-to-speech synthesis."""

import shutil
import sys
import time
from pathlib import Path
from typing import Optional

from pydub import AudioSegment
from tqdm import tqdm

# Check Python version and handle TTS import with better error messages
if sys.version_info < (3, 10):
    raise RuntimeError(
        f"Python 3.10+ is required. Current version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n"
        "Coqui TTS 0.22+ requires Python 3.10 or higher due to dependency requirements."
    )

try:
    from TTS.api import TTS
except ImportError as e:
    error_msg = str(e)
    if "bangla" in error_msg.lower() or "unsupported operand type" in error_msg.lower():
        raise RuntimeError(
            "Failed to import TTS library due to Python version incompatibility.\n"
            f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n"
            "Coqui TTS 0.22+ requires Python 3.10 or higher.\n"
            "Please upgrade Python or use: pip install 'TTS<0.22.0' (may have limited features)"
        ) from e
    raise

from .config import (
    DEFAULT_MODEL,
    FALLBACK_MODEL,
    MAX_CHARS_PER_CHUNK,
    ADD_SILENCE_BETWEEN_CHUNKS,
    LEAD_IN_MS,
    SAMPLE_RATE,
    DEFAULT_SPEAKER_IDX,
    DEFAULT_SPEAKER,
    DEFAULT_LANGUAGE,
)
from .chunking import split_text_into_chunks
from .utils import log_info, log_warning, log_error, make_temp_directory

# Module-level model cache
_tts_model: Optional[TTS] = None
_current_model_name: Optional[str] = None


def get_tts_model(model_name: Optional[str] = None) -> TTS:
    """
    Get or initialize the TTS model (singleton pattern).
    
    Args:
        model_name: Optional model name override. If None, uses DEFAULT_MODEL.
    
    Returns:
        Initialized TTS model instance
    """
    global _tts_model, _current_model_name
    
    target_model = model_name or DEFAULT_MODEL
    
    # Return cached model if it's the same model
    if _tts_model is not None and _current_model_name == target_model:
        return _tts_model
    
    # Try to load the requested model
    try:
        print(f"\n{'='*60}")
        print(f"📦 Loading TTS model: {target_model}")
        print(f"{'='*60}")
        print("⏳ This may take a few minutes on first run (downloading model)...")
        print("   Model size: ~2-3 GB")
        
        start_time = time.time()
        _tts_model = TTS(target_model)
        load_time = time.time() - start_time
        
        _current_model_name = target_model
        print(f"✅ Successfully loaded model in {load_time:.1f} seconds")
        print(f"{'='*60}\n")
        return _tts_model
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        # Check for TOS-related errors
        if "EOF" in error_type or "input" in error_msg.lower() or "tos" in error_msg.lower():
            print(f"\n⚠️  Model requires Terms of Service acceptance:")
            print(f"   XTTS v2 requires interactive TOS acceptance.")
            print(f"   This model cannot be used in non-interactive environments (web apps).")
            print(f"   To use XTTS v2, run the CLI first to accept the TOS.")
            print(f"   Falling back to VITS model instead...\n")
        else:
            print(f"\n⚠️  Failed to load model {target_model}")
            print(f"   Error: {error_type}: {error_msg}\n")
        
        log_warning(f"Failed to load model {target_model}: {error_type}: {error_msg}")
        
        # If it's not the fallback model, try fallback
        if target_model != FALLBACK_MODEL:
            print(f"🔄 Trying fallback model: {FALLBACK_MODEL}")
            print("⏳ Loading fallback model...")
            try:
                start_time = time.time()
                _tts_model = TTS(FALLBACK_MODEL)
                load_time = time.time() - start_time
                _current_model_name = FALLBACK_MODEL
                print(f"✅ Successfully loaded fallback model in {load_time:.1f} seconds\n")
                return _tts_model
            except Exception as e2:
                error_msg2 = str(e2)
                error_type2 = type(e2).__name__
                print(f"\n❌ Fallback model also failed!")
                print(f"   Error: {error_type2}: {error_msg2}")
                print(f"\n💡 Troubleshooting tips:")
                print(f"   1. Check your internet connection (models download on first use)")
                print(f"   2. Ensure you have enough disk space (~2-3 GB per model)")
                print(f"   3. Try running: python cli.py --text 'test' --output test.wav")
                print(f"   4. Check TTS documentation: https://tts.readthedocs.io/")
                log_error(f"Failed to load fallback model {FALLBACK_MODEL}: {error_type2}: {error_msg2}")
                raise RuntimeError(
                    f"Could not load any TTS model.\n"
                    f"Primary ({target_model}): {error_type}: {error_msg}\n"
                    f"Fallback ({FALLBACK_MODEL}): {error_type2}: {error_msg2}"
                )
        else:
            raise RuntimeError(
                f"Could not load TTS model: {target_model}\n"
                f"Error: {error_type}: {error_msg}"
            )


def synthesize_to_wav(text: str, output_path: Path, model_name: Optional[str] = None, speaker_idx: Optional[str] = None) -> None:
    """
    Synthesize text to speech and save as WAV file.
    
    Handles long text by splitting into chunks, generating audio for each,
    and concatenating them into a single output file.
    
    Args:
        text: Input text to synthesize
        output_path: Path where the output WAV file will be saved
        model_name: Optional model name override
        speaker_idx: Optional speaker ID (for multi-speaker models like VCTK)
    """
    print(f"\n{'='*60}")
    print(f"🎙️  Starting TTS Synthesis")
    print(f"{'='*60}")
    print(f"📝 Input text: {len(text)} characters")
    print(f"💾 Output file: {output_path}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get the TTS model
    print(f"\n📦 Getting TTS model...")
    tts = get_tts_model(model_name)
    
    # Split text into chunks
    print(f"\n✂️  Splitting text into chunks...")
    chunks = split_text_into_chunks(text, MAX_CHARS_PER_CHUNK)
    print(f"✅ Split into {len(chunks)} chunk(s)")
    for i, chunk in enumerate(chunks, 1):
        print(f"   Chunk {i}: {len(chunk)} characters")
    
    # Create temporary directory for chunk audio files
    temp_dir = make_temp_directory()
    chunk_files = []
    
    try:
        # Generate audio for each chunk
        is_xtts = "xtts" in _current_model_name.lower() if _current_model_name else False
        is_vctk = "vctk" in _current_model_name.lower() if _current_model_name else False
        
        # Determine speaker to use
        selected_speaker = speaker_idx or DEFAULT_SPEAKER_IDX
        
        print(f"\n🎵 Generating audio for {len(chunks)} chunk(s)...")
        print(f"   Model type: {'XTTS v2' if is_xtts else 'VCTK VITS' if is_vctk else 'VITS'}")
        if is_xtts:
            print(f"   Speaker: {DEFAULT_SPEAKER}, Language: {DEFAULT_LANGUAGE}")
        elif is_vctk:
            print(f"   Speaker: {selected_speaker} (Male storytelling voice)")
        
        # Progress bar for chunk generation
        chunk_progress = tqdm(
            enumerate(chunks, 1),
            total=len(chunks),
            desc="Generating audio",
            unit="chunk",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )
        
        for i, chunk in chunk_progress:
            chunk_progress.set_description(f"Generating chunk {i}/{len(chunks)}")
            chunk_file = temp_dir / f"chunk_{i:04d}.wav"
            
            try:
                chunk_start = time.time()
                if is_xtts:
                    # XTTS v2 requires speaker and language parameters
                    tts.tts_to_file(
                        text=chunk,
                        file_path=str(chunk_file),
                        speaker=DEFAULT_SPEAKER,
                        language=DEFAULT_LANGUAGE,
                    )
                elif is_vctk and hasattr(tts, 'speakers'):
                    # VCTK multi-speaker model uses 'speaker' parameter
                    tts.tts_to_file(
                        text=chunk,
                        file_path=str(chunk_file),
                        speaker=selected_speaker,
                    )
                else:
                    # Single-speaker VITS models use simpler API
                    tts.tts_to_file(text=chunk, file_path=str(chunk_file))
                
                chunk_time = time.time() - chunk_start
                chunk_progress.set_postfix({"time": f"{chunk_time:.1f}s"})
                chunk_files.append(chunk_file)
            except Exception as e:
                chunk_progress.close()
                log_error(f"Error generating audio for chunk {i}: {e}")
                raise
        
        chunk_progress.close()
        print(f"✅ Generated {len(chunk_files)} audio chunk(s)")
        
        # Load and concatenate all chunk audio files
        print(f"\n🔗 Concatenating audio chunks...")
        audio_segments = []
        
        concat_progress = tqdm(
            chunk_files,
            desc="Loading chunks",
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
        )
        
        for chunk_file in concat_progress:
            segment = AudioSegment.from_wav(str(chunk_file))
            audio_segments.append(segment)
            
            # Add silence between chunks if configured
            if ADD_SILENCE_BETWEEN_CHUNKS and chunk_file != chunk_files[-1]:
                silence = AudioSegment.silent(duration=500)  # 500ms silence
                audio_segments.append(silence)
        
        concat_progress.close()
        
        # Combine all segments
        print("   Combining segments...")
        final_audio = sum(audio_segments)
        
        # Add leading silence
        if LEAD_IN_MS > 0:
            print(f"   Adding {LEAD_IN_MS}ms leading silence...")
            leading_silence = AudioSegment.silent(duration=LEAD_IN_MS)
            final_audio = leading_silence + final_audio
        
        # Normalize volume
        print("   Normalizing audio volume...")
        final_audio = final_audio.normalize(headroom=1.0)
        
        # Ensure correct sample rate
        if final_audio.frame_rate != SAMPLE_RATE:
            print(f"   Converting sample rate: {final_audio.frame_rate} → {SAMPLE_RATE} Hz")
            final_audio = final_audio.set_frame_rate(SAMPLE_RATE)
        
        # Export to WAV format (16-bit)
        print(f"   Exporting to WAV format...")
        export_start = time.time()
        final_audio.export(str(output_path), format="wav", parameters=["-ac", "1"])  # Mono audio
        export_time = time.time() - export_start
        
        duration_seconds = len(final_audio) / 1000.0
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully generated audio file!")
        print(f"   📁 File: {output_path}")
        print(f"   ⏱️  Duration: {duration_seconds:.1f} seconds")
        print(f"   💾 Size: {file_size_mb:.2f} MB")
        print(f"   📊 Sample rate: {SAMPLE_RATE} Hz")
        print(f"   ⏳ Export time: {export_time:.1f}s")
        print(f"{'='*60}\n")
        
    finally:
        # Clean up temporary files
        if temp_dir.exists():
            print("🧹 Cleaning up temporary files...")
            shutil.rmtree(temp_dir)


