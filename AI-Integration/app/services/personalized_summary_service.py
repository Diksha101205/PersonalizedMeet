import json
import logging
import time
from typing import Any

from google.genai.errors import ClientError, ServerError
from pydantic import ValidationError

from app.config import settings
from app.models.schemas import PersonalizedSummaryRequest, PersonalizedSummaryResponse
from app.utils.errors import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiQuotaExceededError,
    GeminiUnavailableError,
    InvalidGeminiResponseError,
)

logger = logging.getLogger("uvicorn.error")


class PersonalizedSummaryService:
    """Generate summaries solely from information authorized by the caller."""

    _SYSTEM_INSTRUCTION = """You are generating a personalized meeting summary.

The supplied information has already passed role-based authorization.
Use ONLY the supplied authorized information.
Do not:
- invent information
- infer unauthorized information
- reconstruct restricted information
- mention information that was not supplied
- use outside knowledge
- assume missing details
- make authorization decisions

Generate a concise and accurate summary for the specified participant role.
Return:
- summary
- keyPoints
- decisions
- actionItems

All generated content must be grounded only in the supplied authorized data.

Return ONLY one valid JSON object with exactly these fields:
{
  "participantRole": "<the supplied participant role>",
  "summary": "...",
  "keyPoints": ["..."],
  "decisions": ["..."],
  "actionItems": ["..."]
}
Do not include Markdown fences, prose, or any text outside the JSON object."""
    _RETRY_DELAYS_SECONDS = (2, 4)

    def __init__(self, client: Any | None = None):
        self._client = client

    def generate_summary(
        self, request: PersonalizedSummaryRequest
    ) -> PersonalizedSummaryResponse:
        client = self._get_client()
        payload = self._authorized_payload(request)

        try:
            response = self._generate_content_with_retry(client, payload)
        except ClientError as exc:
            if exc.code == 429:
                logger.error("Gemini summary generation failed (ClientError): quota exhausted")
                raise GeminiQuotaExceededError(
                    "Gemini quota is currently exhausted. Please retry later."
                ) from exc
            logger.error(
                "Gemini summary generation failed (%s): %s",
                type(exc).__name__,
                exc,
            )
            raise GeminiGenerationError("Personalized summary generation failed") from exc
        except ServerError as exc:
            if exc.status == "UNAVAILABLE":
                logger.error(
                    "Gemini summary generation failed (ServerError): provider unavailable"
                )
                raise GeminiUnavailableError(
                    "Gemini provider is temporarily unavailable. Please retry later."
                ) from exc
            logger.error(
                "Gemini summary generation failed (%s): %s",
                type(exc).__name__,
                exc,
            )
            raise GeminiGenerationError("Personalized summary generation failed") from exc
        except Exception as exc:
            logger.error(
                "Gemini summary generation failed (%s): %s",
                type(exc).__name__,
                exc,
            )
            raise GeminiGenerationError("Personalized summary generation failed") from exc

        try:
            summary = PersonalizedSummaryResponse.model_validate_json(response.text)
        except (AttributeError, TypeError, ValidationError, ValueError) as exc:
            raise InvalidGeminiResponseError("Gemini returned an invalid summary response") from exc

        if summary.participantRole != request.participantRole:
            raise InvalidGeminiResponseError("Gemini returned an invalid summary response")

        return summary

    def _generate_content_with_retry(self, client: Any, payload: dict[str, object]) -> Any:
        from google.genai import types

        for delay_seconds in (*self._RETRY_DELAYS_SECONDS, None):
            try:
                return client.models.generate_content(
                    model=settings.gemini_model,
                    contents=json.dumps(payload),
                    config=types.GenerateContentConfig(
                        system_instruction=self._SYSTEM_INSTRUCTION,
                        temperature=0.1,
                    ),
                )
            except ServerError as exc:
                if exc.status != "UNAVAILABLE" or delay_seconds is None:
                    raise
                logger.warning(
                    "Gemini returned 503 UNAVAILABLE; retrying summary generation in %s seconds",
                    delay_seconds,
                )
                time.sleep(delay_seconds)

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if not settings.gemini_api_key:
            raise GeminiConfigurationError("GEMINI_API_KEY is required for personalized summaries")

        try:
            from google import genai
        except ImportError as exc:
            raise GeminiConfigurationError("google-genai is not installed") from exc

        try:
            self._client = genai.Client(api_key=settings.gemini_api_key)
            return self._client
        except Exception as exc:
            raise GeminiConfigurationError("Gemini client could not be configured") from exc

    def _authorized_payload(self, request: PersonalizedSummaryRequest) -> dict[str, object]:
        return {
            "participantRole": request.participantRole.value,
            "authorizedInformation": [
                item.model_dump(mode="json") for item in request.authorizedInformation
            ],
            "authorizedDecisions": request.authorizedDecisions,
            "authorizedActionItems": request.authorizedActionItems,
            "relevantTopics": request.relevantTopics,
            "speakerInformation": (
                [speaker.model_dump(mode="json") for speaker in request.speakerInformation]
                if request.speakerInformation is not None
                else None
            ),
        }
