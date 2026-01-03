import os
import re
import tempfile

import requests
import streamlit as st
from audiorecorder import audiorecorder

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ALLOWED_AUDIO_TYPES = ["mp3", "wav"]

st.set_page_config(page_title="Voicebot", page_icon="🎙️")
st.title("🎙️ Voicebot")
st.markdown("### Please upload an audio file or record your audio.")


def backend_available() -> bool:
    """Check if backend is reachable."""
    try:
        r = requests.get(f"{BACKEND_URL}/keywords", timeout=2)
        return r.ok
    except Exception:
        return False


def display_keywords(keywords: list[str]):
    """Display detected keywords as plain text."""
    if keywords:
        st.markdown(f"**Keywords:** {', '.join(keywords)}")
    else:
        st.markdown("**Keywords:** None")


def highlight_keywords(text: str, keywords: list[str]) -> str:
    """Highlight keywords inline inside the transcribed text using <mark>."""
    for kw in keywords:
        text = re.sub(
            fr"(?i)\b({re.escape(kw)})\b",
            r'<mark style="background-color: yellow">\1</mark>',
            text,
        )
    return text


def send_to_backend(file_name: str, file_obj, mime: str = "application/octet-stream"):
    """Send audio file to backend for transcription and keyword extraction."""
    if not backend_available():
        st.error(f"Backend not reachable at {BACKEND_URL}. Start it or set BACKEND_URL.")
        return

    response = None
    try:
        files = {"audio_file": (file_name, file_obj, mime)}
        response = requests.post(f"{BACKEND_URL}/transcribe", files=files, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Inline highlighted text
        highlighted_text = highlight_keywords(data.get("text", ""), data.get("keywords", []))
        st.markdown(f"**Transcribed Text:** {highlighted_text}", unsafe_allow_html=True)

        # Display keywords as plain text
        display_keywords(data.get("keywords", []))

    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        if response is not None:
            try:
                st.write(f"Details: {response.json().get('error', 'Unknown error')}")
            except Exception:
                st.write(f"Raw response: {response.text}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


# Audio Upload Section
with st.expander("Upload an Audio File"):
    st.header("Upload an Audio File")
    audio_file = st.file_uploader("Choose an audio file", type=ALLOWED_AUDIO_TYPES)

    if audio_file:
        st.audio(audio_file)
        send_to_backend(
            audio_file.name,
            audio_file,
            audio_file.type or "application/octet-stream",
        )

st.markdown("---")

# Audio Recording Section
with st.expander("Record Audio"):
    st.header("Audio Recorder")
    audio = audiorecorder("Click to record", "Click to stop recording")

    if len(audio) > 0:
        raw_bytes = audio.export().read()
        st.audio(raw_bytes)

        # Save recording to a temporary file and send to backend
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            audio.export(tmp.name, format="wav")
            tmp.seek(0)
            send_to_backend("recording.wav", tmp, "audio/wav")
