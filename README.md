# Learn in Sleep TTS

Give text, get voice. Local TTS using Coqui XTTS/VITS. Suitable for long-form narration and sleep/educational videos.

## Requirements

- Python 3.10+
- ffmpeg installed on your system
- espeak-ng (recommended for better phonemization)

### Installing dependencies

**macOS:**
```bash
brew install ffmpeg espeak-ng
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg espeak-ng
```

**Windows:**
```bash
# ffmpeg
choco install ffmpeg

# espeak-ng (optional but recommended)
# Download from: https://github.com/espeak-ng/espeak-ng/releases
```

### Installing ffmpeg only

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use:
```bash
choco install ffmpeg
```

## Installation

1. Clone the repository:
```bash
git clone <REPO_URL>
cd learn_in_sleep_tts
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** 
- The first run will download the TTS model (VITS by default), which may take several minutes and require ~500MB-1GB of disk space.
- **XTTS v2** requires interactive Terms of Service acceptance and cannot be used in web apps. To use XTTS v2, set `TTS_MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2` and run the CLI first to accept the TOS.

## Usage

### Command-Line Interface

Generate audio from inline text:
```bash
python cli.py --text "Hello world, this is a test." --output output.wav
```

Generate audio from a text file:
```bash
python cli.py --input-file script.txt --output script.wav
```

Use a different model:
```bash
python cli.py --text "Hello world" --output output.wav --model "tts_models/en/ljspeech/vits"
```

### Web Interface

Start the web server:
```bash
python web_app.py
```

Or using uvicorn directly:
```bash
uvicorn web_app:app --reload --port 8000
```

Then open your browser to:
```
http://localhost:8000
```

Paste your text into the form, optionally change the filename, and click "Generate Audio" to download the WAV file.

## Configuration

You can configure the TTS engine using environment variables or by editing `learn_in_sleep_tts/config.py`:

- `TTS_MODEL_NAME`: Primary TTS model (default: `tts_models/en/ljspeech/vits`)
  - **Note:** XTTS v2 (`tts_models/multilingual/multi-dataset/xtts_v2`) requires interactive TOS acceptance and won't work in web apps
- `TTS_FALLBACK_MODEL`: Fallback model if primary fails (default: `tts_models/en/ljspeech/tacotron2-DDC`)
- `MAX_CHARS_PER_CHUNK`: Maximum characters per chunk (default: `800`)
- `ADD_SILENCE_BETWEEN_CHUNKS`: Add silence between chunks (default: `False`)
- `LEAD_IN_MS`: Leading silence in milliseconds (default: `500`)
- `SAMPLE_RATE`: Audio sample rate (default: `44100`)
- `DEFAULT_SPEAKER`: XTTS speaker (default: `female-en-5`)
- `DEFAULT_LANGUAGE`: XTTS language (default: `en`)

Create a `.env` file in the project root to set these values:
```
TTS_MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2
MAX_CHARS_PER_CHUNK=800
```

## Features

- **Long text handling**: Automatically splits long text into manageable chunks at sentence boundaries
- **Model fallback**: Automatically falls back to VITS if XTTS fails to load
- **Audio normalization**: Normalizes volume for consistent playback
- **Configurable silence**: Optional leading silence and inter-chunk pauses
- **High-quality output**: 16-bit, 44.1kHz WAV files suitable for production use

## Project Structure

```
learn_in_sleep_tts/
├── README.md
├── requirements.txt
├── cli.py                 # Command-line interface
├── web_app.py             # Web interface (FastAPI)
└── learn_in_sleep_tts/
    ├── __init__.py
    ├── config.py          # Configuration settings
    ├── tts_engine.py      # TTS model and synthesis logic
    ├── chunking.py        # Text chunking utilities
    └── utils.py           # Helper functions
```

## Troubleshooting

**Model download fails:**
- Ensure you have a stable internet connection
- Check available disk space (XTTS v2 requires ~2GB)
- Try using the fallback VITS model: `--model "tts_models/en/ljspeech/vits"`

**Audio generation fails:**
- Verify ffmpeg is installed: `ffmpeg -version`
- Check that you have write permissions for the output directory
- Ensure the input text is not empty

**Web interface not working:**
- Make sure port 8000 is not already in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

## License

This project uses Coqui TTS, which is licensed under the MPL 2.0 License.


