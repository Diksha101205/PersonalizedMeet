from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _comma_separated_setting(name: str, default: str) -> tuple[str, ...]:
    return tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())


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
    default_sensitivity: str = os.getenv("DEFAULT_SENSITIVITY", "INTERNAL")
    public_sensitivity_patterns: tuple[str, ...] = _comma_separated_setting(
        "PUBLIC_SENSITIVITY_PATTERNS", "public"
    )
    internal_sensitivity_patterns: tuple[str, ...] = _comma_separated_setting(
        "INTERNAL_SENSITIVITY_PATTERNS", "internal"
    )
    confidential_sensitivity_patterns: tuple[str, ...] = _comma_separated_setting(
        "CONFIDENTIAL_SENSITIVITY_PATTERNS",
        "confidential,budget,salary,compensation,revenue,profit,cost,pricing,payment,phone number,email,address,personal information,date of birth,legal case,lawsuit,litigation,contract,agreement,legal issue,compliance,employee complaint,disciplinary,termination,resignation,performance review,acquisition,merger,confidential strategy,unreleased product,business plan,expansion plan,internal strategy",
    )
    financial_sensitivity_patterns: tuple[str, ...] = _comma_separated_setting(
        "FINANCIAL_SENSITIVITY_PATTERNS",
        "budget,salary,compensation,revenue,profit,cost,pricing,payment,financial figures",
    )
    restricted_sensitivity_patterns: tuple[str, ...] = _comma_separated_setting(
        "RESTRICTED_SENSITIVITY_PATTERNS",
        "restricted,strictly confidential,highly confidential,password,api key,access token,private key,security key,credential,account number",
    )
    allowed_recording_roots: tuple[Path, ...] = tuple(
        Path(path).expanduser().resolve()
        for path in os.getenv("ALLOWED_RECORDING_ROOTS", "").split(os.pathsep)
        if path.strip()
    )


settings = Settings()
