from app.models.schemas import SpeakerTranscriptSegment
from app.services.diarization_service import DiarizationSegment
from app.services.transcription_service import TranscriptionSegment


class TranscriptService:
    def align_segments(
            self,
            transcription_segments: list[TranscriptionSegment],
            diarization_segments: list[DiarizationSegment],
    ) -> list[SpeakerTranscriptSegment]:
        aligned_segments: list[SpeakerTranscriptSegment] = []

        for transcription in transcription_segments:
            speaker = self._find_best_speaker(transcription, diarization_segments)
            aligned_segments.append(
                SpeakerTranscriptSegment(
                    speaker=speaker,
                    startTime=round(transcription.start, 3),
                    endTime=round(transcription.end, 3),
                    text=transcription.text,
                )
            )

        return aligned_segments

    def _find_best_speaker(
            self,
            transcription: TranscriptionSegment,
            diarization_segments: list[DiarizationSegment],
    ) -> str:
        best_speaker = "UNKNOWN_SPEAKER"
        best_overlap = 0.0

        for diarization in diarization_segments:
            overlap = self._overlap_seconds(
                transcription.start,
                transcription.end,
                diarization.start,
                diarization.end,
            )
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diarization.speaker

        return best_speaker

    def _overlap_seconds(self, start_a: float, end_a: float, start_b: float, end_b: float) -> float:
        return max(0.0, min(end_a, end_b) - max(start_a, start_b))
