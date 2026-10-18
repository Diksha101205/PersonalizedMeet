from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.models.schemas import ParticipantRole, PersonalizedSummaryResponse
from app.routes import personalized_summary_routes
from app.utils.errors import (
    GeminiQuotaExceededError,
    GeminiUnavailableError,
    InvalidGeminiResponseError,
)


class FakePersonalizedSummaryService:
    def generate_summary(self, request):
        return PersonalizedSummaryResponse(
            participantRole=request.participantRole,
            summary="Authorized summary.",
            keyPoints=["Authorized point."],
            decisions=request.authorizedDecisions,
            actionItems=request.authorizedActionItems,
        )


class FailingPersonalizedSummaryService:
    def __init__(self, error):
        self.error = error

    def generate_summary(self, request):
        raise self.error


def valid_payload(role: str = "MANAGER") -> dict[str, object]:
    return {
        "participantRole": role,
        "authorizedInformation": [],
        "authorizedDecisions": ["Authorized decision."],
        "authorizedActionItems": ["Authorized action item."],
        "relevantTopics": ["authorized topic"],
    }


def test_endpoint_generates_a_summary_from_a_valid_manager_request(monkeypatch):
    monkeypatch.setattr(
        personalized_summary_routes,
        "personalized_summary_service",
        FakePersonalizedSummaryService(),
    )
    client = TestClient(app)

    response = client.post("/api/generate-personalized-summary", json=valid_payload())

    assert response.status_code == 200
    assert response.json()["participantRole"] == ParticipantRole.MANAGER.value
    assert response.json()["summary"] == "Authorized summary."


def test_endpoint_accepts_a_valid_participant_request(monkeypatch):
    monkeypatch.setattr(
        personalized_summary_routes,
        "personalized_summary_service",
        FakePersonalizedSummaryService(),
    )
    client = TestClient(app)

    response = client.post(
        "/api/generate-personalized-summary", json=valid_payload("PARTICIPANT")
    )

    assert response.status_code == 200
    assert response.json()["participantRole"] == ParticipantRole.PARTICIPANT.value


def test_endpoint_rejects_requests_missing_required_authorized_fields():
    response = TestClient(app).post(
        "/api/generate-personalized-summary", json={"participantRole": "MANAGER"}
    )

    assert response.status_code == 422


def test_endpoint_is_registered_in_openapi():
    paths = TestClient(app).get("/openapi.json").json()["paths"]

    assert "/api/generate-personalized-summary" in paths


@pytest.mark.parametrize(
    ("error", "status_code", "message"),
    [
        (
            GeminiQuotaExceededError("Gemini quota is currently exhausted. Please retry later."),
            429,
            "Gemini quota is currently exhausted. Please retry later.",
        ),
        (
            GeminiUnavailableError("Gemini provider is temporarily unavailable. Please retry later."),
            503,
            "Gemini provider is temporarily unavailable. Please retry later.",
        ),
        (
            InvalidGeminiResponseError("Gemini returned an invalid summary response"),
            502,
            "Gemini returned an invalid summary response",
        ),
    ],
)
def test_endpoint_returns_the_expected_safe_gemini_error(
    monkeypatch, error, status_code, message
):
    monkeypatch.setattr(
        personalized_summary_routes,
        "personalized_summary_service",
        FailingPersonalizedSummaryService(error),
    )

    response = TestClient(app).post("/api/generate-personalized-summary", json=valid_payload())

    assert response.status_code == status_code
    assert response.json() == {"message": message}
