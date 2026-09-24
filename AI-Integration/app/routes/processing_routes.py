from fastapi import APIRouter

from app.models.schemas import ProcessRecordingRequest, ProcessRecordingResponse
from app.services.diarization_service import DiarizationService
from app.services.transcript_service import TranscriptService
from app.services.transcription_service import TranscriptionService
from app.utils.audio import extracted_wav, validate_recording_path

router = APIRouter(prefix="/api", tags=["recording-processing"])

transcription_service = TranscriptionService()
diarization_service = DiarizationService()
transcript_service = TranscriptService()


@router.post("/process-recording", response_model=ProcessRecordingResponse)
def process_recording(request: ProcessRecordingRequest):
    recording_path = validate_recording_path(request.filePath)
    with extracted_wav(recording_path) as audio_path:
        transcription_segments = transcription_service.transcribe(audio_path)
        diarization_segments = diarization_service.diarize(audio_path)

    speaker_segments = transcript_service.align_segments(transcription_segments, diarization_segments)

    return ProcessRecordingResponse(
        recordingId=request.recordingId,
        segments=speaker_segments,
    )
