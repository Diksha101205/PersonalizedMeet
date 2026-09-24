from dataclasses import dataclass
from pathlib import Path

from app.config import settings
from app.utils.errors import DiarizationError, ModelConfigurationError


@dataclass(frozen=True)
class DiarizationSegment:
    start: float
    end: float
    speaker: str


class DiarizationService:
    def __init__(self):
        self._pipeline = None

    def diarize(self, recording_path: Path) -> list[DiarizationSegment]:
        pipeline = self._get_pipeline()
        try:
            diarization = pipeline(str(recording_path))
            segments: list[DiarizationSegment] = []
            for turn, _track, speaker in diarization.itertracks(yield_label=True):
                segments.append(
                    DiarizationSegment(
                        start=float(turn.start),
                        end=float(turn.end),
                        speaker=str(speaker),
                    )
                )
            return segments
        except Exception as exc:
            raise DiarizationError("Speaker diarization failed") from exc

    def _get_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        if not settings.huggingface_token:
            raise ModelConfigurationError(
                "HUGGINGFACE_TOKEN is required for pyannote speaker diarization."
            )

        try:
            from pyannote.audio import Pipeline
        except ImportError as exc:
            raise ModelConfigurationError(
                "pyannote.audio is not installed. Install requirements and use Python 3.10 or 3.11."
            ) from exc

        try:
            self._pipeline = Pipeline.from_pretrained(
                settings.pyannote_model,
                use_auth_token=settings.huggingface_token,
            )
            return self._pipeline
        except Exception as exc:
            raise ModelConfigurationError("Pyannote diarization model could not be loaded") from exc
