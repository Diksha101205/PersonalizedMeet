from dataclasses import dataclass
from pathlib import Path

from app.config import settings
from app.utils.errors import ModelConfigurationError, TranscriptionError


@dataclass(frozen=True)
class TranscriptionSegment:
    start: float
    end: float
    text: str
    confidence: float | None = None


class TranscriptionService:
    def __init__(self):
        self._model = None

    def transcribe(self, recording_path: Path) -> list[TranscriptionSegment]:
        model = self._get_model()
        try:
            segments, _info = model.transcribe(str(recording_path), beam_size=5)
            return [
                TranscriptionSegment(
                    start=float(segment.start),
                    end=float(segment.end),
                    text=segment.text.strip(),
                    confidence=None,
                )
                for segment in segments
                if segment.text and segment.text.strip()
            ]
        except Exception as exc:
            raise TranscriptionError("Speech-to-text transcription failed") from exc

    def _get_model(self):
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise ModelConfigurationError(
                "faster-whisper is not installed. Install requirements and use Python 3.10 or 3.11."
            ) from exc

        try:
            self._model = WhisperModel(
                settings.whisper_model_size,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
            return self._model
        except Exception as exc:
            raise ModelConfigurationError("Whisper model could not be loaded") from exc
