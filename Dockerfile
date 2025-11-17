FROM python:3.9-slim

# Avoid Python buffering logs
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies (FFmpeg is needed by pydub / audio processing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy entire project into the image
COPY . .

# Default command (can be overridden by docker-compose)
# Here we default to the backend; docker-compose will override for each service.
CMD ["python", "backend/api_server.py"]