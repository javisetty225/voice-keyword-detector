import os
import streamlit as st
import requests
from audiorecorder import audiorecorder
import tempfile

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

st.title("Voicebot")

def display_keywords(keywords):
    """Displays the detected keywords as colored buttons."""
    if keywords:
        buttons = ' '.join(
            f'<button style="background-color: yellow; padding: 5px; margin: 2px; border: none; border-radius: 5px; cursor: pointer; animation: flash 1.5s infinite;">{keyword}</button>'
            for keyword in keywords
        )
        st.markdown(
            f'<div style="display: flex; align-items: center; flex-wrap: wrap;"><strong>Keywords:</strong>&nbsp;{buttons}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("Keywords:")

st.markdown("### Please upload an audio file or record your audio.")

# File uploader section
with st.expander("Upload an Audio File"):
    st.header("Upload an Audio File")
    audio_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])

    if audio_file:
        st.audio(audio_file)
        try:
            files = {
                "file": (audio_file.name, audio_file, audio_file.type or "application/octet-stream")
            }
            response = requests.post(f"{BACKEND_URL}/transcribe", files=files)
            response.raise_for_status()
            result = response.json()
            st.markdown(f"**Transcribed Text:** {result['text']}")
            display_keywords(result["keywords"])
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            if "response" in locals() and response is not None:
                try:
                    st.write(f"Error details: {response.json().get('error', 'Unknown error')}")
                except Exception:
                    st.write(f"Error details (raw): {response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Divider for better visual separation
st.markdown("---")

# Audio recorder section
with st.expander("Record Audio"):
    st.header("Audio Recorder")
    audio = audiorecorder("Click to record", "Click to stop recording")

    if len(audio) > 0:
        st.audio(audio.export().read())
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            audio.export(tmpfile.name, format="wav")
            tmpfile.flush()
            tmpfile.seek(0)
            try:
                response = requests.post(f"{BACKEND_URL}/transcribe", files={"file": tmpfile})
                response.raise_for_status()
                result = response.json()
                st.markdown(f"**Transcribed Text:** {result['text']}")
                display_keywords(result["keywords"])
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
                if response.content:
                    st.write(f"Error details: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# CSS for flashing animation
st.markdown("""
<style>
@keyframes flash {
  0% { background-color: yellow; }
  50% { background-color: lightyellow; }
  100% { background-color: yellow; }
}
</style>
""", unsafe_allow_html=True)
