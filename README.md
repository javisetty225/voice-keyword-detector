# VoiceBot

Lightweight speech-to-text + keyword extraction service with a FastAPI backend and Streamlit UI.

## Architecture
- Backend: FastAPI (`backend/api_server.py`) serving ASR + keyword detection.
- Frontend: Streamlit (`frontend/web_app.py`) simple UI for upload and display.
- Tests: PyTest in `tests/`.
- Models/keywords: `backend/keywords.json`.

## Features
- Upload audio (wav/mp3/ogg) -> automatic conversion -> transcription.
- Keyword detection from configurable list.
- Docker + local dev workflows.
- Mockable components for fast tests.

## Tech Stack
Python 3.12, FastAPI, Streamlit, Pydub, PyTest, Uvicorn, Docker.

## Project Structure

```
voicebot/
├── backend/
│   ├── app_server.py
│   ├── keywords.json
│  
├── frontend/
│   ├── web_app.py
│    
├── tests/
│   ├── test_api_server.py
│   ├── test_keywords.py
│
├── docker-compose.yml
    Dockerfile
    pyproject.toml
    uv.lock
    README.md
```

### Root

- **Dockerfile**: Dockerfile for building the frontend and backend container.
- **docker-compose.yml**: Docker Compose file to run the backend and frontend services.

### Installation & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nagajavisetty/voicebot.git
   cd voicebot
   ```

2. **Build and run the containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: [http://localhost:8080](http://localhost:8080)

### Usage

1. **Upload an audio file:**
   - Open the frontend at [http://localhost:8080](http://localhost:8080).
   - Upload an audio file (MP3 or WAV format).
   - The transcribed text and detected keywords will be displayed.

2. **View results:**
   - The transcribed text is shown on the page.
   - Detected keywords are highlighted with colored buttons.

### Configuration

- **keywords.json**: Update this file to modify the list of keywords to be detected. Example format:
  ```json
  {
      "keywords": ["rot", "blau", "England"]
  }
  ```

### Example

To test the application, you can use any German language audio file. The backend will transcribe the audio and detect the specified keywords, displaying the results on the frontend.

### Troubleshooting

- Ensure Docker and Docker Compose are installed and running correctly.
- Verify that the ports `5000` (backend) and `8080` (frontend) are not being used by other applications.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

