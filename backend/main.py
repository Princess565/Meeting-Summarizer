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

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key)

# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI()

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
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# ----------------------------
# Load Whisper (Tiny for Cloud)
# ----------------------------
whisper_model = whisper.load_model("tiny")

# ----------------------------
# Utility Functions
# ----------------------------
def extract_audio(video_path, audio_path):
    try:
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

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            raise Exception("FFmpeg failed")

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Audio extraction failed."}
        )


def transcribe_audio(audio_path):
    try:
        result = whisper_model.transcribe(audio_path)
        return result["text"]
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Transcription failed."}
        )


# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def root():
    return {"message": "Meeting Summarizer API Running"}


# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------
# Summarize Endpoint
# ----------------------------
@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):

    try:
        # Unique filename
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_FOLDER / unique_name

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract audio
        audio_path = UPLOAD_FOLDER / f"{unique_name}.wav"
        extract_audio(str(file_path), str(audio_path))

        # Transcribe audio
        transcript = transcribe_audio(str(audio_path))

        # ----------------------------
        # Gemini Prompt
        # ----------------------------
        prompt = f"""
You are an AI meeting analyzer.

Return ONLY valid JSON in this format:

{{
  "summary": "string",
  "action_items": [
    {{
      "task": "string",
      "speaker": "string",
      "timestamp": "string"
    }}
  ],
  "key_questions": [
    {{
      "question": "string",
      "speaker": "string",
      "timestamp": "string"
    }}
  ],
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

        # Remove markdown formatting if Gemini returns ```json
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "")
            raw_text = raw_text.replace("```", "")
            raw_text = raw_text.strip()

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "AI returned invalid JSON.",
                    "raw_output": raw_text
                }
            )

        return {
            "summary": result.get("summary", ""),
            "action_items": result.get("action_items", []),
            "key_questions": result.get("key_questions", []),
            "transcript": transcript,
            "speakers": result.get("speakers", [])
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )