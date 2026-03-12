import uuid
import os
import json
import shutil
import subprocess
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
import whisper

# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)

# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI(title="Meeting Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ----------------------------
# Load Whisper Model
# ----------------------------
whisper_model = whisper.load_model("tiny")

# ----------------------------
# Extract Audio with FFmpeg
# ----------------------------
def extract_audio(video_path: str, audio_path: str):

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]

    result = subprocess.run(command, capture_output=True)

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail="Audio extraction failed"
        )

# ----------------------------
# Transcribe Audio
# ----------------------------
def transcribe_audio(audio_path: str):

    try:
        result = whisper_model.transcribe(audio_path)
        return result["text"]

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Transcription failed"
        )

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def root():
    return {"message": "Meeting Summarizer API Running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------------------
# Summarize Endpoint
# ----------------------------
@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):

    unique_name = f"{uuid.uuid4()}_{file.filename}"

    video_path = UPLOAD_DIR / unique_name
    audio_path = UPLOAD_DIR / f"{unique_name}.wav"

    try:

        # Save uploaded file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract audio
        extract_audio(str(video_path), str(audio_path))

        # Transcribe audio
        transcript = transcribe_audio(str(audio_path))

        # Prompt for Gemini
        prompt = f"""
Return ONLY valid JSON.

{{
  "summary": "string",
  "action_items": [],
  "key_questions": [],
  "speakers": []
}}

Transcript:
{transcript}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw_text)

        return {
            "summary": result.get("summary", ""),
            "action_items": result.get("action_items", []),
            "key_questions": result.get("key_questions", []),
            "speakers": result.get("speakers", []),
            "transcript": transcript
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:

        # Clean temporary files
        for path in [video_path, audio_path]:
            if path.exists():
                os.remove(path)