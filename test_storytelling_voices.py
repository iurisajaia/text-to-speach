#!/usr/bin/env python3
"""Generate voice samples for Middle-Aged Male storytelling voices.
Matches preferences: Male, Middle-Aged, American, High-Quality, Narrative & Story.
"""

from learn_in_sleep_tts.tts_engine import synthesize_to_wav
from pathlib import Path

# Test text optimized for storytelling/narrative
test_text = """Once upon a time, in a quiet little town, there lived a storyteller whose voice could captivate anyone who listened. 
His words flowed like a gentle stream, carrying listeners on a journey through tales of adventure, mystery, and wonder. 
This is a test of the narrative storytelling voice."""

# Middle-Aged Male voices best suited for Narrative & Storytelling
storytelling_voices = [
    ("p225", "Warm Storytelling Voice (Default & Best Match)"),
    ("p228", "Rich, Warm Narrative Voice"),
    ("p229", "Professional Storyteller"),
    ("p232", "Calm, Soothing Narrator"),
    ("p233", "Authoritative Storyteller"),
    ("p234", "Engaging Narrative Voice"),
    ("p245", "Clear, Professional Storyteller"),
    ("p247", "Balanced Narrative Voice"),
    ("p248", "Warm, Expressive Storyteller"),
    ("p250", "Mature Narrative Voice"),
    ("p251", "Deep, Resonant Storyteller"),
    ("p252", "Professional Narrative Voice"),
    ("p253", "Rich, Engaging Storyteller"),
    ("p254", "Warm Narrative Voice"),
    ("p255", "Clear Storyteller"),
]

print("=" * 70)
print("🎙️  Generating Voice Samples for Storytelling")
print("=" * 70)
print(f"Preferences: Male | Middle-Aged | American | High-Quality | Narrative & Story")
print(f"Test text: {len(test_text)} characters")
print(f"Generating {len(storytelling_voices)} voice samples...")
print("=" * 70)

samples_dir = Path("voice_samples")
samples_dir.mkdir(exist_ok=True)

for speaker_id, description in storytelling_voices:
    output_file = samples_dir / f"storytelling_{speaker_id}.wav"
    print(f"\n🎵 Generating: {speaker_id} - {description}")
    try:
        synthesize_to_wav(test_text, output_file, speaker_idx=speaker_id)
        print(f"✅ Saved: {output_file}")
    except Exception as e:
        print(f"❌ Error with {speaker_id}: {e}")

print("\n" + "=" * 70)
print("✅ All voice samples generated!")
print(f"📁 Samples saved in: {samples_dir.absolute()}")
print("💡 Listen to the samples to find your preferred storytelling voice.")
print("=" * 70)

