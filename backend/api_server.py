import os
import time
import json
import logging
import tempfile
from flask import Flask, request, jsonify
import torch
from transformers import pipeline
from pydub import AudioSegment

app = Flask(__name__)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load pipeline
try:
    pipe = pipeline("automatic-speech-recognition", model="bofenghuang/whisper-medium-cv11-german", device=device)
    pipe.model.config.forced_decoder_ids = pipe.tokenizer.get_decoder_prompt_ids(language="de", task="transcribe")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise e

# Load keywords from config
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KEYWORDS_PATH = os.path.join(BASE_DIR, "keywords.json")
    with open(KEYWORDS_PATH, encoding="utf-8") as f:
        keywords = json.load(f)["keywords"]
    keyword_set = {k.lower() for k in keywords}
    logger.info("Keywords loaded successfully")
except Exception as e:
    logger.error(f"Error loading keywords: {e}")
    raise e

def transcribe_audio(file_path):
    """Transcribes audio from the given file path."""
    try:
        generated_sentences = pipe(file_path)["text"]
        return generated_sentences
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise e

def detect_keywords(text: str) -> list[str]:
    """Detects and returns keywords present in the given text."""
    detected: list[str] = []
    for word in text.split():
        cleaned_word = word.strip(".,!?:;").lower()
        if cleaned_word in keyword_set:
            detected.append(word.strip(".,!?:;"))  # Preserve original case
    return detected

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Endpoint to transcribe audio and detect keywords."""
    start_time = time.time()
    try:
        if 'file' not in request.files:
            logger.error("No file part in the request")
            return jsonify({"error": "No file provided"}), 400
        file = request.files['file']
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith(('.wav', '.mp3')):
            logger.error("Unsupported file format")
            return jsonify({"error": "Unsupported file format"}), 400

        with tempfile.TemporaryDirectory() as tmpdirname:
            audio_path = os.path.join(tmpdirname, file.filename)
            file.save(audio_path)

            logger.info(f"File saved to {audio_path}")
            convert_start_time = time.time()
            audio = AudioSegment.from_file(audio_path)
            audio.export(audio_path, format="wav")
            logger.info(f"Audio conversion time: {time.time() - convert_start_time}")

            transcribe_start_time = time.time()
            text = transcribe_audio(audio_path)
            logger.info(f"Transcription time: {time.time() - transcribe_start_time}")

            detect_start_time = time.time()
            detected_keywords = detect_keywords(text)
            logger.info(f"Keyword detection time: {time.time() - detect_start_time}")

            total_time = time.time() - start_time
            logger.info(f"Total processing time: {total_time}")

            return jsonify({"text": text, "keywords": detected_keywords})
    except Exception as e:
        logger.error(f"Error in /transcribe endpoint: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
