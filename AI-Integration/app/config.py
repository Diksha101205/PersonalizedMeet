from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "PersonalizedMeet AI Integration"
    whisper_model_size: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    whisper_device: str = os.getenv("WHISPER_DEVICE", "cpu")
    whisper_compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    pyannote_model: str = os.getenv("PYANNOTE_MODEL", "pyannote/speaker-diarization-3.1")
    huggingface_token: str | None = os.getenv("HUGGINGFACE_TOKEN")
    ffmpeg_path: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    allowed_recording_roots: tuple[Path, ...] = tuple(
        Path(path).expanduser().resolve()
        for path in os.getenv("ALLOWED_RECORDING_ROOTS", "").split(os.pathsep)
        if path.strip()
    )


settings = Settings()
