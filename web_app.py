#!/usr/bin/env python3
"""Web interface for Learn in Sleep TTS using FastAPI."""

import sys
import tempfile
from pathlib import Path

# Check Python version before importing TTS
if sys.version_info < (3, 10):
    print("ERROR: Python 3.10 or higher is required.")
    print(f"Current Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    sys.exit(1)

try:
    from fastapi import FastAPI, Form, HTTPException
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles

    from learn_in_sleep_tts.tts_engine import synthesize_to_wav
    from learn_in_sleep_tts.utils import log_info, log_error
except ImportError as e:
    if "TTS" in str(e) or "bangla" in str(e):
        print("ERROR: Failed to import TTS library.")
        print("This is likely due to Python version incompatibility.")
        print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("\nCoqui TTS 0.22+ requires Python 3.10 or higher.")
        sys.exit(1)
    raise

app = FastAPI(title="Learn in Sleep TTS")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML form."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Learn in Sleep TTS</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-top: 0;
            }
            label {
                display: block;
                margin-top: 20px;
                margin-bottom: 5px;
                font-weight: 600;
                color: #555;
            }
            textarea {
                width: 100%;
                min-height: 200px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                font-family: inherit;
                resize: vertical;
                box-sizing: border-box;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                box-sizing: border-box;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
                transition: background-color 0.2s;
            }
            button:hover {
                background-color: #0056b3;
            }
            button:disabled {
                background-color: #ccc;
                cursor: not-allowed;
            }
            .info {
                margin-top: 20px;
                padding: 10px;
                background-color: #e7f3ff;
                border-left: 4px solid #007bff;
                border-radius: 4px;
                font-size: 14px;
                color: #555;
            }
            .error {
                margin-top: 20px;
                padding: 10px;
                background-color: #ffe7e7;
                border-left: 4px solid #dc3545;
                border-radius: 4px;
                font-size: 14px;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Learn in Sleep TTS</h1>
            <p>Enter text below to generate a voice file using Coqui TTS.</p>
            
            <form id="ttsForm" method="post" action="/synthesize">
                <label for="text">Text to synthesize:</label>
                <textarea id="text" name="text" required placeholder="Enter your text here..."></textarea>
                
                <label for="speaker">Voice/Speaker (Male, Middle-Aged, American, High-Quality, Narrative & Story):</label>
                <select id="speaker" name="speaker" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box;">
                    <optgroup label="🎙️ Middle-Aged Male - Narrative & Storytelling">
                        <option value="p229" selected>👨 p229 - Professional Storyteller (Default)</option>
                        <option value="p234">👨 p234 - Engaging Narrative Voice</option>
                        <option value="p253">👨 p253 - Rich, Engaging Storyteller</option>
                        <option value="p254">👨 p254 - Warm Narrative Voice</option>
                        <option value="p255">👨 p255 - Clear Storyteller</option>
                        <option value="p258">👨 p258 - Mature, Engaging Storyteller</option>
                        <option value="p262">👨 p262 - Rich Storytelling Voice</option>
                    </optgroup>
                </select>
                <small style="color: #666; display: block; margin-top: 5px;">💡 Filtered for: Male | Middle-Aged | American Accent | High-Quality | Narrative & Story. Default: p229 (Professional Storyteller).</small>
                
                <label for="filename">Output filename:</label>
                <input type="text" id="filename" name="filename" value="output.wav" placeholder="output.wav">
                
                <button type="submit" id="submitBtn">Generate Audio</button>
            </form>
            
            <div id="message"></div>
        </div>
        
        <script>
            const form = document.getElementById('ttsForm');
            const submitBtn = document.getElementById('submitBtn');
            const messageDiv = document.getElementById('message');
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                submitBtn.disabled = true;
                submitBtn.textContent = 'Generating...';
                messageDiv.innerHTML = '<div class="info">Generating audio, please wait...</div>';
                
                try {
                    const response = await fetch('/synthesize', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = formData.get('filename') || 'output.wav';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                        
                        messageDiv.innerHTML = '<div class="info">✓ Audio generated successfully! Download started.</div>';
                    } else {
                        const errorText = await response.text();
                        messageDiv.innerHTML = `<div class="error">Error: ${errorText}</div>`;
                    }
                } catch (error) {
                    messageDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Generate Audio';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/synthesize")
async def synthesize(text: str = Form(...), filename: str = Form("output.wav"), speaker: str = Form(None)):
    """
    Synthesize text to speech and return the WAV file.
    
    Args:
        text: Text to synthesize (required)
        filename: Output filename (optional, defaults to output.wav)
        speaker: Speaker ID for multi-speaker models (optional)
    
    Returns:
        WAV file as FileResponse
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Ensure filename ends with .wav
    if not filename.endswith(".wav"):
        filename = filename + ".wav"
    
    # Use default speaker from config if none provided or empty
    from learn_in_sleep_tts.config import DEFAULT_SPEAKER_IDX
    # Ensure we always use a male, middle-aged, American, storytelling voice
    selected_speaker = speaker.strip() if speaker and speaker.strip() else DEFAULT_SPEAKER_IDX
    
    log_info(f"Web request: synthesizing {len(text)} characters with speaker {selected_speaker}")
    
    # Create temporary file for output
    temp_file = Path(tempfile.gettempdir()) / f"tts_output_{tempfile.gettempprefix()}.wav"
    
    try:
        # Generate audio
        synthesize_to_wav(text, temp_file, speaker_idx=selected_speaker)
        
        # Return file as download
        return FileResponse(
            path=temp_file,
            filename=filename,
            media_type="audio/wav",
        )
    except Exception as e:
        log_error(f"Error during synthesis: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")
    finally:
        # Note: FileResponse will handle cleanup, but we could also clean up here
        # if needed. For now, we'll let the OS handle temp file cleanup.
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


