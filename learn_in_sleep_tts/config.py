"""Configuration settings for the TTS engine."""

import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration
# Note: XTTS v2 requires interactive TOS acceptance, so we use VCTK VITS as default (multi-speaker)
# Set TTS_MODEL_NAME env var to use XTTS v2 if you've accepted the TOS
DEFAULT_MODEL = os.getenv("TTS_MODEL_NAME", "tts_models/en/vctk/vits")
# Fallback to a simpler model if VCTK fails
FALLBACK_MODEL = os.getenv("TTS_FALLBACK_MODEL", "tts_models/en/ljspeech/vits")

# Chunking configuration
MAX_CHARS_PER_CHUNK = int(os.getenv("MAX_CHARS_PER_CHUNK", "800"))

# Audio configuration
ADD_SILENCE_BETWEEN_CHUNKS = os.getenv("ADD_SILENCE_BETWEEN_CHUNKS", "False").lower() == "true"
LEAD_IN_MS = int(os.getenv("LEAD_IN_MS", "500"))
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "44100"))

# Voice/Speaker configuration
# Preferences: Male | Middle-Aged | American Accent | Narrative & Story
# For VCTK model: p225-p376 are male speakers, p225 is the best match for storytelling
# For XTTS v2: use speaker names like "female-en-5", "male-en-1", etc.
DEFAULT_SPEAKER_IDX = os.getenv("DEFAULT_SPEAKER_IDX", "p229")  # Male, Middle-Aged, American, Narrative & Story
DEFAULT_SPEAKER = os.getenv("DEFAULT_SPEAKER", "male-en-1")  # For XTTS v2 (changed to male)
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")


