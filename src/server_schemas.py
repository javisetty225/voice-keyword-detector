from pydantic import BaseModel, ConfigDict, Field


class TranscribeResponse(BaseModel):
    """
    Response returned after successful audio transcription.
    """

    text: str = Field(description="Transcribed text extracted from the audio file.")
    keywords: list[str] = Field(description="Detected predefined keywords found in the transcribed text.")
    timings: dict[str, float] = Field(description="Processing time statistics in seconds.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "I am going to the Berlin to eat pizza",
                "keywords": ["Berlin", "pizza"],
                "timings": {
                    "conversion_sec": 0.145,
                    "asr_sec": 6.034,
                    "keyword_sec": 0,
                    "total_sec": 6.179
                }
            }
        }
    )


class KeywordsResponse(BaseModel):
    """
    Response containing all predefined keywords.
    """

    keywords: list[str] = Field(description="List of predefined keywords used for detection.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keywords": ["Berlin", "pizza"],
            }
        }
    )
