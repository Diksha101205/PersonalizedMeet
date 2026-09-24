from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from app.routes import processing_routes
from app.models.schemas import ProcessRecordingRequest
from app.services.diarization_service import DiarizationSegment
from app.services.transcription_service import TranscriptionSegment


def test_process_recording_reuses_extracted_wav_for_transcription_and_diarization(monkeypatch):
    recording_path = Path("recording.mp4")
    wav_path = Path("extracted.wav")
    received_paths = []

    @contextmanager
    def fake_extracted_wav(path):
        assert path == recording_path
        yield wav_path

    monkeypatch.setattr(processing_routes, "validate_recording_path", lambda file_path: recording_path)
    monkeypatch.setattr(processing_routes, "extracted_wav", fake_extracted_wav)
    monkeypatch.setattr(
        processing_routes,
        "transcription_service",
        SimpleNamespace(
            transcribe=lambda path: received_paths.append(("transcription", path))
            or [TranscriptionSegment(start=0.0, end=1.0, text="Hello.")]
        ),
    )
    monkeypatch.setattr(
        processing_routes,
        "diarization_service",
        SimpleNamespace(
            diarize=lambda path: received_paths.append(("diarization", path))
            or [DiarizationSegment(start=0.0, end=1.0, speaker="SPEAKER_00")]
        ),
    )

    response = processing_routes.process_recording(
        ProcessRecordingRequest(recordingId=123, filePath="C:/uploads/recording.mp4")
    )

    assert response.recordingId == 123
    assert response.segments[0].speaker == "SPEAKER_00"
    assert received_paths == [
        ("transcription", wav_path),
        ("diarization", wav_path),
    ]
