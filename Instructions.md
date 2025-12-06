You are my coding assistant.
Create a complete, minimal, production-ready Python project called learn_in_sleep_tts that lets me input text and get a generated voice file using Coqui TTS (XTTS v2 or VITS).

I want:

Simple installation

One command-line entry point

Optional small web UI (FastAPI + HTML form)

Clean structure, no overengineering

1. Project goals

Build a Python project that:

Installs with pip install -r requirements.txt.

Lets me run a CLI command like:

python cli.py --text "Hello world" --output output.wav


OR

python cli.py --input-file script.txt --output output.wav


Optionally starts a small local web server:

python web_app.py


Where I can:

open http://localhost:8000

paste text into a textarea

click a button

get a generated .wav file for download.

Uses Coqui TTS with XTTS v2 model by default:

Model name: tts_models/multilingual/multi-dataset/xtts_v2

Fallback to tts_models/en/ljspeech/vits if XTTS fails or isn’t available.

Handles long text:

Split into safe chunks by sentence boundaries

Avoid super long chunks (e.g. max 800–1000 chars)

Generate audio per chunk

Concatenate into one final WAV file.

Produces audio suitable for sleep/educational narration:

Normalized volume

Optional small silence at start and between chunks

16-bit, 44.1kHz WAV output.

2. Tech stack & dependencies

Use:

Python 3.10+

TTS (Coqui TTS library)

pydub for joining WAV chunks

fastapi + uvicorn for the web UI

python-dotenv for simple env config (optional)

Create requirements.txt with pinned versions where reasonable.

Example (adjust exact versions as needed):

TTS

pydub

fastapi

uvicorn

python-dotenv

Assume ffmpeg is installed on the system for pydub to work (document that in README).

3. Project structure

Create this structure:

learn_in_sleep_tts/
  README.md
  requirements.txt
  cli.py
  web_app.py
  learn_in_sleep_tts/
    __init__.py
    config.py
    tts_engine.py
    chunking.py
    utils.py


What each file should do:

README.md

Explain what the project does

How to install

How to run CLI

How to run web app

Mention ffmpeg requirement

config.py

Default config values:

DEFAULT_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

FALLBACK_MODEL = "tts_models/en/ljspeech/vits"

MAX_CHARS_PER_CHUNK = 800

ADD_SILENCE_BETWEEN_CHUNKS = False (bool)

LEAD_IN_MS = 500 (0.5s)

SAMPLE_RATE = 44100

Maybe read env variables if present (e.g. TTS_MODEL_NAME).

chunking.py

Function to split long text into reasonable chunks.

Rules:

Normalize whitespace

Prefer splitting on .?! boundaries

Avoid splitting mid-word

Ensure no chunk exceeds MAX_CHARS_PER_CHUNK.

Example API:

def split_text_into_chunks(text: str, max_chars: int) -> list[str]:
    ...


tts_engine.py

Encapsulate TTS model loading & audio generation.

Responsibilities:

Lazy-load the model once (singleton style) to avoid reloading every call.

Provide synthesize_to_wav(text: str, output_path: Path) that:

Splits text into chunks using chunking.split_text_into_chunks

For each chunk, generates a temporary WAV file

Concatenates all temporary WAV files using pydub

Adds small leading silence

Optional silence between chunks if enabled in config

Normalizes the final audio

Saves to output_path

Cleans up temp files.

For XTTS (xtts_v2), pass:

speaker="female-en-5" (or similar default)

language="en"

For VITS fallback, just call tts_to_file with text + file path.

Handle exceptions:

If XTTS model fails to load, log a warning and fall back to VITS model automatically.

utils.py

Simple helpers:

Logging wrapper (print with prefixes)

Make temp directory

Path helpers.

cli.py

Use argparse to support:

--text "..." (inline text)

--input-file path/to/file.txt

--output path/to/file.wav (required)

--model (optional override)

Rules:

Exactly one of --text or --input-file must be provided.

Read text from the chosen source.

Call tts_engine.synthesize_to_wav.

Print informative messages: chunks count, output path, etc.

Example usage:

python cli.py --text "Hello world" --output output.wav
python cli.py --input-file script.txt --output script.wav


web_app.py

Build a minimal FastAPI app:

GET / → HTML page with:

<textarea name="text">

<input type="text" name="filename"> default: output.wav

Submit button.

POST /synthesize:

Accepts form data text (required), filename (optional).

Calls tts_engine.synthesize_to_wav.

Returns the generated WAV file as a FileResponse so it downloads.

Run with:

uvicorn web_app:app --reload --port 8000


Keep HTML simple but not ugly: just a basic form, nothing fancy.

4. Implementation details

Chunking behavior:

In chunking.split_text_into_chunks:

Normalize whitespace: text = " ".join(text.split())

Use regex to split into sentences first:

re.split(r"(?<=[\.\?\!])\s+", text)

Rebuild chunks with a simple greedy algorithm:

Start an empty current string

Add sentences until adding another would exceed max_chars

Push current into chunks, reset, continue

Ensure no empty chunks.

TTS Engine behavior:

In tts_engine.py:

On first import / init, load model into a module-level variable.

Expose a function like:

def get_tts_model(model_name: str = None) -> TTS:
    ...


So we can reuse it between calls.

Use tempfile or a local tmp_chunks/ directory for chunk WAVs.

Join using pydub.AudioSegment.

Normalize volume using audio.normalize(headroom=1.0).

Use SAMPLE_RATE from config if needed.

5. README content

In README.md, include:

Short project description:

“Give text, get voice. Local TTS using Coqui XTTS/VITS. Suitable for long-form narration and sleep/educational videos.”

Requirements:

Python 3.10+

ffmpeg installed (show example install commands for macOS (brew) and Ubuntu (apt)).

Installation:

git clone <REPO_URL>
cd learn_in_sleep_tts
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


CLI usage examples.

Web usage example.

6. Code quality

Use type hints where it makes sense.

Keep functions short and readable.

Add docstrings to main functions (split_text_into_chunks, synthesize_to_wav, etc.).

No unnecessary abstraction layers.

7. Final check

When you finish:

Show me:

requirements.txt

cli.py

web_app.py

learn_in_sleep_tts/tts_engine.py

learn_in_sleep_tts/chunking.py

learn_in_sleep_tts/config.py

Make sure:

Running python cli.py --text "Test" --output test.wav works.

Running uvicorn web_app:app --port 8000 gives a working web form to generate wav.

Build everything now according to this spec.

You can paste all of that into Cursor as your “big instruction prompt” and let it scaffold + implement the project. After it’s done, you just:

python cli.py --text "Hello from my new TTS project" --output hello.wav


and you’re ready to use it for your scripts.