from pathlib import Path
from types import SimpleNamespace

import pytest

from app.utils import audio
from app.utils.errors import AudioExtractionError


def test_extracted_wav_runs_ffmpeg_once_and_cleans_up(tmp_path, monkeypatch):
    recording_path = tmp_path / "meeting.mp4"
    recording_path.write_bytes(b"fake video")
    calls = []

    def fake_run(command, capture_output, text, check, shell):
        calls.append(
            {
                "command": command,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "shell": shell,
            }
        )
        Path(command[-1]).write_bytes(b"fake wav")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(audio, "settings", SimpleNamespace(ffmpeg_path="ffmpeg-test"))
    monkeypatch.setattr(audio.subprocess, "run", fake_run)

    with audio.extracted_wav(recording_path) as wav_path:
        assert wav_path.exists()
        assert wav_path.suffix == ".wav"

    assert len(calls) == 1
    assert calls[0]["command"][:3] == ["ffmpeg-test", "-y", "-i"]
    assert calls[0]["command"][3] == str(recording_path)
    assert calls[0]["command"][-8:-1] == [
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
    ]
    assert calls[0]["shell"] is False
    assert not wav_path.exists()


def test_extracted_wav_reports_missing_ffmpeg(tmp_path, monkeypatch):
    recording_path = tmp_path / "meeting.webm"
    recording_path.write_bytes(b"fake video")

    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(audio, "settings", SimpleNamespace(ffmpeg_path="missing-ffmpeg"))
    monkeypatch.setattr(audio.subprocess, "run", fake_run)

    with pytest.raises(AudioExtractionError, match="FFmpeg executable was not found"):
        with audio.extracted_wav(recording_path):
            pass


def test_extracted_wav_reports_conversion_failure(tmp_path, monkeypatch):
    recording_path = tmp_path / "meeting.mp4"
    recording_path.write_bytes(b"fake video")

    def fake_run(command, **kwargs):
        return SimpleNamespace(returncode=1, stderr="bad input")

    monkeypatch.setattr(audio, "settings", SimpleNamespace(ffmpeg_path="ffmpeg-test"))
    monkeypatch.setattr(audio.subprocess, "run", fake_run)

    with pytest.raises(AudioExtractionError, match="FFmpeg audio extraction failed"):
        with audio.extracted_wav(recording_path):
            pass
