# Voicebot

The Voicebot project converts spoken German into text and detects specific keywords.  
It consists of a Flask backend for speech recognition and a Streamlit frontend for interaction.  
Both services are containerized using Docker and orchestrated with Docker Compose.

## Features

- Transcribe German speech to text using a Hugging Face Whisper-based model.
- Detect configured keywords in the transcribed text.
- Upload or record audio via a web interface.
- Highlight detected keywords in the UI.

## Project Structure

```
voicebot/
├── backend/
│   ├── app.py
│   ├── keywords.json
│  
│   
├── frontend/
│   ├── frontend.py
│ 
│   
├── docker-compose.yml
    Dockerfile
    requirements.txt
```

### Backend

- **api_server.py**: Main application file for the Flask backend.
- **keywords.json**: Configuration file containing the keywords to be detected.

### Frontend

- **frontend.py**: Main application file for the Streamlit frontend.
- **requirements.txt**: Python dependencies for the frontend.

### Root

- **Dockerfile**: Dockerfile for building the frontend and backend container.
- **docker-compose.yml**: Docker Compose file to run the backend and frontend services.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

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

---

This README file provides a comprehensive guide to setting up, running, and using the Voicebot project. It includes information on the project structure, installation steps, usage instructions, and troubleshooting tips.