from pathlib import Path
import subprocess
import tempfile
from contextlib import contextmanager
from collections.abc import Iterator

from app.config import settings
from app.utils.errors import AudioExtractionError, InvalidRecordingError, RecordingNotFoundError

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".webm", ".avi"}


def validate_recording_path(file_path: str) -> Path:
    path = Path(file_path).expanduser().resolve()

    if not path.exists() or not path.is_file():
        raise RecordingNotFoundError("Recording file was not found")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise InvalidRecordingError("Unsupported recording format")

    if settings.allowed_recording_roots:
        is_allowed = any(path.is_relative_to(root) for root in settings.allowed_recording_roots)
        if not is_allowed:
            raise InvalidRecordingError("Recording path is outside the allowed recording directories")

    return path


@contextmanager
def extracted_wav(recording_path: Path) -> Iterator[Path]:
    temp_file = tempfile.NamedTemporaryFile(prefix="personalizedmeet-", suffix=".wav", delete=False)
    wav_path = Path(temp_file.name)
    temp_file.close()

    try:
        _convert_to_wav(recording_path, wav_path)
        yield wav_path
    finally:
        try:
            wav_path.unlink(missing_ok=True)
        except OSError:
            pass


def _convert_to_wav(recording_path: Path, wav_path: Path) -> None:
    command = [
        settings.ffmpeg_path,
        "-y",
        "-i",
        str(recording_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(wav_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
    except FileNotFoundError as exc:
        raise AudioExtractionError(
            "FFmpeg executable was not found. Install FFmpeg or set FFMPEG_PATH."
        ) from exc
    except OSError as exc:
        raise AudioExtractionError("FFmpeg audio extraction could not be started") from exc

    if result.returncode != 0:
        raise AudioExtractionError("FFmpeg audio extraction failed")
