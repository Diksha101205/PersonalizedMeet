from collections import Counter
import re

from app.config import settings
from app.models.schemas import (
    MeetingInformation,
    MeetingStatement,
    SpeakerTranscript,
    SpeakerTranscriptSegment,
    TimestampedTranscriptSegment,
)


class InformationExtractionService:
    """Build deterministic, transcript-derived meeting metadata after alignment."""

    _WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z'-]*")

    def build_speaker_transcripts(
        self, segments: list[SpeakerTranscriptSegment]
    ) -> list[SpeakerTranscript]:
        grouped_segments: dict[str, list[SpeakerTranscriptSegment]] = {}

        for segment in sorted(segments, key=lambda item: (item.startTime, item.endTime)):
            grouped_segments.setdefault(segment.speaker, []).append(segment)

        return [
            SpeakerTranscript(
                speaker=speaker,
                segments=[
                    TimestampedTranscriptSegment(
                        startTime=segment.startTime,
                        endTime=segment.endTime,
                        text=segment.text,
                    )
                    for segment in speaker_segments
                ],
                fullTranscript=" ".join(
                    segment.text.strip() for segment in speaker_segments if segment.text.strip()
                ),
            )
            for speaker, speaker_segments in grouped_segments.items()
        ]

    def extract_meeting_information(
        self, segments: list[SpeakerTranscriptSegment]
    ) -> MeetingInformation:
        ordered_segments = sorted(segments, key=lambda item: (item.startTime, item.endTime))
        return MeetingInformation(
            topics=self._extract_topics(ordered_segments),
            decisions=self._extract_statements(ordered_segments, settings.decision_patterns),
            actionItems=self._extract_statements(ordered_segments, settings.action_item_patterns),
            peopleMentioned=self._extract_people_mentioned(ordered_segments),
        )

    def _extract_topics(self, segments: list[SpeakerTranscriptSegment]) -> list[str]:
        words = (
            word.lower()
            for segment in segments
            for word in self._WORD_PATTERN.findall(segment.text)
            if len(word) >= 4 and word.lower() not in settings.topic_stop_words
        )
        counts = Counter(words)
        return sorted(
            word
            for word, count in counts.items()
            if count >= settings.topic_min_occurrences
        )

    def _extract_statements(
        self,
        segments: list[SpeakerTranscriptSegment],
        patterns: tuple[str, ...],
    ) -> list[MeetingStatement]:
        expression = self._compile_patterns(patterns)
        return [
            MeetingStatement(
                text=segment.text,
                speaker=segment.speaker,
                startTime=segment.startTime,
                endTime=segment.endTime,
            )
            for segment in segments
            if expression.search(segment.text)
        ]

    def _compile_patterns(self, patterns: tuple[str, ...]) -> re.Pattern[str]:
        escaped_patterns = [
            re.escape(pattern).replace(r"\ ", r"\s+") for pattern in patterns
        ]
        return re.compile(
            "|".join(rf"\b{pattern}\b" for pattern in escaped_patterns),
            re.IGNORECASE,
        )

    def _extract_people_mentioned(self, segments: list[SpeakerTranscriptSegment]) -> list[str]:
        # Named-entity recognition is intentionally deferred to avoid guessing names.
        return []
