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
    topic_stop_words: frozenset[str] = frozenset(
        word.strip().lower()
        for word in os.getenv(
            "TOPIC_STOP_WORDS",
            "about,after,again,also,and,are,been,being,but,can,could,for,from,have,into,just,more,not,our,out,should,that,the,their,there,they,this,was,were,what,when,will,with,would,you,your",
        ).split(",")
        if word.strip()
    )
    topic_min_occurrences: int = int(os.getenv("TOPIC_MIN_OCCURRENCES", "2"))
    decision_patterns: tuple[str, ...] = tuple(
        pattern.strip()
        for pattern in os.getenv(
            "DECISION_PATTERNS",
            "decided,approved,agreed,finalized,confirmed,will proceed,we will,it was decided",
        ).split(",")
        if pattern.strip()
    )
    action_item_patterns: tuple[str, ...] = tuple(
        pattern.strip()
        for pattern in os.getenv(
            "ACTION_ITEM_PATTERNS",
            "will do,need to,needs to,should,assigned to,responsible for,please,by tomorrow,by Monday",
        ).split(",")
        if pattern.strip()
    )
    allowed_recording_roots: tuple[Path, ...] = tuple(
        Path(path).expanduser().resolve()
        for path in os.getenv("ALLOWED_RECORDING_ROOTS", "").split(os.pathsep)
        if path.strip()
    )


settings = Settings()
