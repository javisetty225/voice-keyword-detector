import json
import logging
import os
import re
import tempfile
import time

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydub import AudioSegment
from transformers import pipeline

from src.backend.server_schemas import KeywordsResponse, TranscribeResponse

MODEL_NAME = os.getenv("ASR_MODEL", "bofenghuang/whisper-medium-cv11-german")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
ALLOWED_EXT = {".wav", ".mp3"}
KEYWORDS_PATH = os.getenv("KEYWORDS_PATH", os.path.join(os.path.dirname(__file__), "keywords.json"))
PIPELINE_TASK = "automatic-speech-recognition"

# Logging
logger = logging.getLogger("voicebot")
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO
)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
keyword_set: set[str] = set()
word_pattern = re.compile(r"\b[\wäöüÄÖÜß]+\b", re.UNICODE)


def load_keywords() -> list[str]:
    """Load keywords from JSON file and populate the keyword set."""
    global keyword_set
    try:
        with open(KEYWORDS_PATH, encoding="utf-8") as f:
            keywords_raw = json.load(f).get("keywords", [])
        keyword_list = [k.lower() for k in keywords_raw]
        keyword_set = set(keyword_list)  # <--- initialize global set
        logger.info("Loaded %d keywords", len(keyword_list))
        return keyword_list
    except Exception:
        logger.exception("Failed to load keywords")
        keyword_set = set()
        return []


def get_asr_pipeline():
    """Load and return the ASR pipeline."""
    try:
        logger.info("Loading ASR model '%s' on %s", MODEL_NAME, device)
        asr_pipe = pipeline(PIPELINE_TASK, model=MODEL_NAME, device=device)
        try:
            forced = asr_pipe.tokenizer.get_decoder_prompt_ids(
                language="de", task="transcribe"
            )
            asr_pipe.model.config.forced_decoder_ids = forced
        except Exception:
            logger.warning("Forced decoder ids not set")
        logger.info("ASR model ready")
        return asr_pipe
    except Exception:
        logger.exception("ASR model load failed")
        raise RuntimeError("Model initialization failed")


def detect_keywords(text: str) -> list[str]:
    """Detect keywords in the transcribed text."""
    found: list[str] = []
    for token in word_pattern.findall(text.lower()):
        if token in keyword_set and token not in found:
            found.append(token)
    return found


def validate_file_meta(upload: UploadFile) -> None:
    ext = os.path.splitext(upload.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Unsupported file extension")


def ensure_size_limit(size_bytes: int) -> None:
    if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")


def register_chatbot_routes(app: FastAPI):
    """Register endpoints for voicebot."""

    @app.on_event("startup")
    def startup_event():
        load_keywords()

    @app.get("/keywords", response_model=KeywordsResponse)
    def list_keywords():
        return KeywordsResponse(keywords=sorted(load_keywords()))

    @app.post("/transcribe", response_model=TranscribeResponse)
    async def transcribe(audio_file: UploadFile = File(...)):
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Empty filename")

        validate_file_meta(audio_file)

        start = time.time()
        try:
            contents = await audio_file.read()
            ensure_size_limit(len(contents))

            with tempfile.TemporaryDirectory() as tmpdir:
                raw_path = os.path.join(tmpdir, audio_file.filename)
                with open(raw_path, "wb") as f:
                    f.write(contents)

                # Convert to WAV
                conv_start = time.time()
                audio = AudioSegment.from_file(raw_path)
                wav_path = os.path.join(tmpdir, "audio.wav")
                audio.export(wav_path, format="wav")
                conv_time = time.time() - conv_start

                # Transcribe
                asr_start = time.time()
                pipe = get_asr_pipeline()
                result = pipe(wav_path)
                text = result.get("text", "").strip()
                asr_time = time.time() - asr_start

                # Detect keywords
                kw_start = time.time()
                detected = detect_keywords(text)
                kw_time = time.time() - kw_start

            total = time.time() - start
            return TranscribeResponse(
                text=text,
                keywords=detected,
                timings={
                    "conversion_sec": round(conv_time, 3),
                    "asr_sec": round(asr_time, 3),
                    "keyword_sec": round(kw_time, 3),
                    "total_sec": round(total, 3),
                },
            )

        except HTTPException:
            raise
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception:
            logger.exception("Transcription failed")
            raise HTTPException(status_code=500, detail="Internal Server Error")
