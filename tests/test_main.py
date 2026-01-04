import io

import pytest
from fastapi.testclient import TestClient

from src.backend import server_endpoints
from src.backend.main import create_app

STATUS_OK = 200
STATUS_BAD_REQUEST = 400
STATUS_UNPROCESSABLE_ENTITY = 422


@pytest.fixture
def client():
    return TestClient(create_app())


def test_transcribe_missing_file(client):
    response = client.post("/transcribe")
    assert response.status_code == STATUS_UNPROCESSABLE_ENTITY


def test_transcribe_unsupported_format(client):
    fake_audio = io.BytesIO(b"fake data")

    response = client.post(
        "/transcribe",
        files={"audio_file": ("test.txt", fake_audio, "text/plain")},
    )

    assert response.status_code == STATUS_BAD_REQUEST
    assert response.json()["detail"] == "Unsupported file extension"


def test_transcribe_valid_audio_mocked(client, monkeypatch):
    # --- mock ASR pipeline factory ---
    def mock_get_asr_pipeline():
        return lambda _: {"text": "Hallo Welt"}

    monkeypatch.setattr(
        server_endpoints,
        "get_asr_pipeline",
        mock_get_asr_pipeline,
    )

    # --- mock audio decoding ---
    class MockAudio:
        def export(self, *_args, **_kwargs):
            pass

    monkeypatch.setattr(
        server_endpoints.AudioSegment,
        "from_file",
        lambda *_args, **_kwargs: MockAudio(),
    )

    fake_audio = io.BytesIO(b"fake wav data")

    response = client.post(
        "/transcribe",
        files={"audio_file": ("test.wav", fake_audio, "audio/wav")},
    )

    assert response.status_code == STATUS_OK

    data = response.json()
    assert data["text"] == "Hallo Welt"
    assert "keywords" in data
    assert "timings" in data

