import json
import logging
from types import SimpleNamespace

import pytest
from google.genai.errors import ClientError, ServerError

from app.models.schemas import (
    ClassifiedInformationItem,
    ParticipantRole,
    PersonalizedSummaryRequest,
    SensitivityLevel,
)
from app.services.personalized_summary_service import PersonalizedSummaryService
from app.utils.errors import (
    GeminiGenerationError,
    GeminiQuotaExceededError,
    GeminiUnavailableError,
    InvalidGeminiResponseError,
)


def make_request(role: ParticipantRole = ParticipantRole.MANAGER) -> PersonalizedSummaryRequest:
    return PersonalizedSummaryRequest(
        participantRole=role,
        authorizedInformation=[
            ClassifiedInformationItem(
                text="The restructuring will begin next month.",
                speaker="SPEAKER_03",
                startTime=120.5,
                endTime=126.2,
                sensitivity=SensitivityLevel.CONFIDENTIAL,
            )
        ],
        authorizedDecisions=["The restructuring will begin next month."],
        authorizedActionItems=["Managers should prepare transition plans."],
        relevantTopics=["team restructuring", "transition planning"],
        speakerInformation=[{"speaker": "SPEAKER_03"}],
    )


def response_text(role: ParticipantRole) -> str:
    return json.dumps(
        {
            "participantRole": role.value,
            "summary": "The meeting covered team restructuring.",
            "keyPoints": ["Restructuring begins next month."],
            "decisions": ["The restructuring will begin next month."],
            "actionItems": ["Managers should prepare transition plans."],
        }
    )


class FakeClient:
    def __init__(self, response: object | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[dict[str, object]] = []
        self.models = self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


class SequencedFakeClient(FakeClient):
    def __init__(self, outcomes: list[object]):
        super().__init__()
        self.outcomes = outcomes

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def unavailable_error() -> ServerError:
    return ServerError(
        503,
        {"error": {"code": 503, "status": "UNAVAILABLE", "message": "high demand"}},
    )


@pytest.mark.parametrize("role", [ParticipantRole.MANAGER, ParticipantRole.PARTICIPANT])
def test_generates_valid_summary_for_authorized_role(role):
    client = FakeClient(response=SimpleNamespace(text=response_text(role)))

    result = PersonalizedSummaryService(client=client).generate_summary(make_request(role))

    assert result.participantRole == role
    assert result.summary == "The meeting covered team restructuring."
    assert result.decisions == ["The restructuring will begin next month."]


def test_empty_authorized_data_is_sent_and_returns_a_valid_response():
    request = PersonalizedSummaryRequest(
        participantRole=ParticipantRole.PARTICIPANT,
        authorizedInformation=[],
        authorizedDecisions=[],
        authorizedActionItems=[],
        relevantTopics=[],
    )
    client = FakeClient(response=SimpleNamespace(text=response_text(ParticipantRole.PARTICIPANT)))

    result = PersonalizedSummaryService(client=client).generate_summary(request)
    payload = json.loads(client.calls[0]["contents"])

    assert result.participantRole == ParticipantRole.PARTICIPANT
    assert payload["authorizedInformation"] == []
    assert payload["authorizedDecisions"] == []
    assert payload["authorizedActionItems"] == []


def test_only_authorized_request_data_is_sent_to_gemini():
    request = make_request()
    client = FakeClient(response=SimpleNamespace(text=response_text(ParticipantRole.MANAGER)))

    PersonalizedSummaryService(client=client).generate_summary(request)

    payload = json.loads(client.calls[0]["contents"])
    assert set(payload) == {
        "participantRole",
        "authorizedInformation",
        "authorizedDecisions",
        "authorizedActionItems",
        "relevantTopics",
        "speakerInformation",
    }
    assert payload["authorizedInformation"][0]["text"] == "The restructuring will begin next month."
    assert "filteredInformation" not in payload
    assert "classifiedInformation" not in payload
    assert "RESTRICTED DETAIL" not in client.calls[0]["contents"]
    config = client.calls[0]["config"]
    assert config.response_mime_type is None
    assert config.response_schema is None


def test_gemini_failure_uses_a_safe_application_error():
    client = FakeClient(error=RuntimeError("provider failed"))

    with pytest.raises(GeminiGenerationError, match="Personalized summary generation failed"):
        PersonalizedSummaryService(client=client).generate_summary(make_request())


def test_unavailable_server_error_retries_and_returns_a_successful_summary(monkeypatch):
    client = SequencedFakeClient(
        [unavailable_error(), SimpleNamespace(text=response_text(ParticipantRole.MANAGER))]
    )
    delays: list[int] = []
    monkeypatch.setattr(
        "app.services.personalized_summary_service.time.sleep", delays.append
    )

    result = PersonalizedSummaryService(client=client).generate_summary(make_request())

    assert result.summary == "The meeting covered team restructuring."
    assert len(client.calls) == 2
    assert delays == [2]


def test_repeated_unavailable_server_errors_exhaust_retries(monkeypatch, caplog):
    client = SequencedFakeClient([unavailable_error(), unavailable_error(), unavailable_error()])
    delays: list[int] = []
    monkeypatch.setattr(
        "app.services.personalized_summary_service.time.sleep", delays.append
    )

    with caplog.at_level(logging.ERROR, logger="uvicorn.error"):
        with pytest.raises(GeminiUnavailableError, match="temporarily unavailable"):
            PersonalizedSummaryService(client=client).generate_summary(make_request())

    assert len(client.calls) == 3
    assert delays == [2, 4]
    final_errors = [record for record in caplog.records if record.levelno == logging.ERROR]
    assert len(final_errors) == 1
    assert "ServerError" in final_errors[0].getMessage()
    assert "provider unavailable" in final_errors[0].getMessage()
    assert "restructuring" not in final_errors[0].getMessage()


def test_non_503_error_is_not_retried(monkeypatch):
    client = SequencedFakeClient(
        [
            ClientError(
                429,
                {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "quota"}},
            )
        ]
    )
    sleep_calls: list[int] = []
    monkeypatch.setattr(
        "app.services.personalized_summary_service.time.sleep", sleep_calls.append
    )

    with pytest.raises(GeminiQuotaExceededError, match="quota is currently exhausted"):
        PersonalizedSummaryService(client=client).generate_summary(make_request())

    assert len(client.calls) == 1
    assert sleep_calls == []


@pytest.mark.parametrize(
    "text",
    [
        "not json",
        "{}",
        "```json\n" + response_text(ParticipantRole.MANAGER) + "\n```",
    ],
)
def test_malformed_gemini_response_is_rejected(text):
    client = FakeClient(response=SimpleNamespace(text=text))

    with pytest.raises(InvalidGeminiResponseError, match="invalid summary response"):
        PersonalizedSummaryService(client=client).generate_summary(make_request())


def test_gemini_response_must_preserve_the_requested_role():
    client = FakeClient(response=SimpleNamespace(text=response_text(ParticipantRole.HOST)))

    with pytest.raises(InvalidGeminiResponseError, match="invalid summary response"):
        PersonalizedSummaryService(client=client).generate_summary(make_request())
