import os
import uuid
import tempfile
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global TTS model
tts_model = None
OUTPUT_DIR = Path("/tmp/tts_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_model():
    global tts_model
    try:
        from TTS.api import TTS
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading XTTS-v2 Romanian model on {device}...")
        tts_model = TTS("eduardem/xtts-v2-romanian").to(device)
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(title="Romanian TTS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": tts_model is not None}

@app.post("/tts")
async def text_to_speech(
    text: str = Form(...),
    voice_sample: UploadFile = File(...),
):
    if tts_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Text too long (max 2000 chars)")

    # Save uploaded voice sample
    suffix = Path(voice_sample.filename).suffix if voice_sample.filename else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_voice:
        content = await voice_sample.read()
        tmp_voice.write(content)
        voice_path = tmp_voice.name

    # Output path
    output_filename = f"{uuid.uuid4()}.wav"
    output_path = OUTPUT_DIR / output_filename

    try:
        logger.info(f"Generating TTS for text ({len(text)} chars)...")
        tts_model.tts_to_file(
            text=text,
            speaker_wav=voice_path,
            language="ro",
            file_path=str(output_path),
        )
        logger.info("TTS generation complete.")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
    finally:
        os.unlink(voice_path)

    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Output file not generated")

    return FileResponse(
        path=str(output_path),
        media_type="audio/wav",
        filename="output.wav",
        headers={"X-Output-File": output_filename},
    )
