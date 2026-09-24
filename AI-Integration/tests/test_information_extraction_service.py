from app.models.schemas import SpeakerTranscriptSegment
from app.services.information_extraction_service import InformationExtractionService


def test_build_speaker_transcripts_groups_and_sorts_segments_chronologically():
    segments = [
        SpeakerTranscriptSegment(speaker="SPEAKER_02", startTime=30.0, endTime=34.2, text="Later update."),
        SpeakerTranscriptSegment(speaker="SPEAKER_01", startTime=20.1, endTime=25.4, text="Second point."),
        SpeakerTranscriptSegment(speaker="SPEAKER_01", startTime=0.0, endTime=12.08, text="First point."),
    ]

    speakers = InformationExtractionService().build_speaker_transcripts(segments)

    assert [speaker.speaker for speaker in speakers] == ["SPEAKER_01", "SPEAKER_02"]
    assert [segment.startTime for segment in speakers[0].segments] == [0.0, 20.1]
    assert speakers[0].fullTranscript == "First point. Second point."


def test_empty_segments_produce_empty_speakers_and_meeting_information():
    service = InformationExtractionService()

    assert service.build_speaker_transcripts([]) == []
    assert service.extract_meeting_information([]).model_dump() == {
        "topics": [],
        "decisions": [],
        "actionItems": [],
        "peopleMentioned": [],
    }


def test_extracts_repeated_topics_and_preserves_decision_and_action_source_segments():
    segments = [
        SpeakerTranscriptSegment(
            speaker="SPEAKER_01",
            startTime=10.0,
            endTime=12.0,
            text="We agreed the budget proposal is ready.",
        ),
        SpeakerTranscriptSegment(
            speaker="SPEAKER_02",
            startTime=13.0,
            endTime=16.0,
            text="Please finalize the budget by Monday.",
        ),
        SpeakerTranscriptSegment(
            speaker="SPEAKER_01",
            startTime=17.0,
            endTime=19.0,
            text="The budget will proceed after review.",
        ),
    ]

    information = InformationExtractionService().extract_meeting_information(segments)

    assert information.topics == ["budget"]
    assert [statement.text for statement in information.decisions] == [
        "We agreed the budget proposal is ready.",
        "The budget will proceed after review.",
    ]
    assert information.decisions[0].speaker == "SPEAKER_01"
    assert information.decisions[0].startTime == 10.0
    assert [statement.text for statement in information.actionItems] == [
        "Please finalize the budget by Monday.",
    ]


def test_does_not_invent_people_or_decisions_or_action_items():
    segments = [
        SpeakerTranscriptSegment(
            speaker="SPEAKER_01",
            startTime=0.0,
            endTime=2.0,
            text="The dashboard has a blue header.",
        )
    ]

    information = InformationExtractionService().extract_meeting_information(segments)

    assert information.decisions == []
    assert information.actionItems == []
    assert information.peopleMentioned == []
