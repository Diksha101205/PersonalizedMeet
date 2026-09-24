from app.services.diarization_service import DiarizationSegment
from app.services.transcript_service import TranscriptService
from app.services.transcription_service import TranscriptionSegment


def test_alignment_assigns_transcript_to_speaker_with_largest_overlap():
    transcription_segments = [
        TranscriptionSegment(start=0.0, end=5.7, text="Good morning everyone."),
        TranscriptionSegment(start=6.3, end=12.2, text="The expansion proposal is ready."),
    ]
    diarization_segments = [
        DiarizationSegment(start=0.0, end=5.8, speaker="SPEAKER_00"),
        DiarizationSegment(start=6.2, end=12.4, speaker="SPEAKER_01"),
    ]

    result = TranscriptService().align_segments(transcription_segments, diarization_segments)

    assert result[0].speaker == "SPEAKER_00"
    assert result[0].text == "Good morning everyone."
    assert result[0].startTime == 0.0
    assert result[0].endTime == 5.7
    assert result[1].speaker == "SPEAKER_01"
    assert result[1].text == "The expansion proposal is ready."


def test_alignment_uses_unknown_speaker_when_no_overlap_exists():
    transcription_segments = [
        TranscriptionSegment(start=20.0, end=22.0, text="No diarization overlap."),
    ]
    diarization_segments = [
        DiarizationSegment(start=0.0, end=5.0, speaker="SPEAKER_00"),
    ]

    result = TranscriptService().align_segments(transcription_segments, diarization_segments)

    assert result[0].speaker == "UNKNOWN_SPEAKER"
