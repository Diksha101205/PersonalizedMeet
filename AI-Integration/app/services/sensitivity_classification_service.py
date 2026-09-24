import re

from app.config import settings
from app.models.schemas import (
    ClassifiedInformationItem,
    MeetingInformation,
    MeetingStatement,
    SensitivityLevel,
)


class SensitivityClassificationService:
    """Classify extracted decisions and action items with transparent rules."""

    _PRIORITY = {
        SensitivityLevel.PUBLIC: 0,
        SensitivityLevel.INTERNAL: 1,
        SensitivityLevel.CONFIDENTIAL: 2,
        SensitivityLevel.RESTRICTED: 3,
    }
    _FINANCIAL_FIGURE_PATTERN = re.compile(
        r"(?:\u20b9|\b(?:inr|usd|eur|rs\.?)\b)\s*\d|\b\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|crore|crores|million|billion|thousand)\b",
        re.IGNORECASE,
    )

    def classify_information(
        self, meeting_information: MeetingInformation
    ) -> list[ClassifiedInformationItem]:
        statements = self._unique_statements(
            [*meeting_information.decisions, *meeting_information.actionItems]
        )
        return [self.classify_statement(statement) for statement in statements]

    def classify_statement(self, statement: MeetingStatement) -> ClassifiedInformationItem:
        text = statement.text.strip()
        candidates: list[SensitivityLevel] = []

        if self._contains_any(text, settings.public_sensitivity_patterns):
            candidates.append(SensitivityLevel.PUBLIC)
        if self._contains_any(text, settings.internal_sensitivity_patterns):
            candidates.append(SensitivityLevel.INTERNAL)
        if self._contains_any(text, settings.confidential_sensitivity_patterns):
            candidates.append(SensitivityLevel.CONFIDENTIAL)
        if self._contains_any(text, settings.restricted_sensitivity_patterns):
            candidates.append(SensitivityLevel.RESTRICTED)
        if self._contains_financial_figure(text):
            candidates.append(SensitivityLevel.RESTRICTED)
        if not candidates:
            candidates.append(self._default_sensitivity())

        return ClassifiedInformationItem(
            text=statement.text,
            speaker=statement.speaker,
            startTime=statement.startTime,
            endTime=statement.endTime,
            sensitivity=max(candidates, key=self._PRIORITY.__getitem__),
        )

    def _default_sensitivity(self) -> SensitivityLevel:
        try:
            return SensitivityLevel(settings.default_sensitivity.upper())
        except ValueError:
            return SensitivityLevel.INTERNAL

    def _contains_financial_figure(self, text: str) -> bool:
        return (
            self._contains_any(text, settings.financial_sensitivity_patterns)
            and self._FINANCIAL_FIGURE_PATTERN.search(text) is not None
        )

    def _contains_any(self, text: str, patterns: tuple[str, ...]) -> bool:
        return any(self._contains_phrase(text, pattern) for pattern in patterns)

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        escaped_phrase = re.escape(phrase).replace(r"\ ", r"\s+")
        return re.search(rf"\b{escaped_phrase}\b", text, re.IGNORECASE) is not None

    def _unique_statements(self, statements: list[MeetingStatement]) -> list[MeetingStatement]:
        seen: set[tuple[str, str, float, float]] = set()
        unique_statements: list[MeetingStatement] = []
        for statement in statements:
            identity = (statement.text, statement.speaker, statement.startTime, statement.endTime)
            if identity not in seen:
                seen.add(identity)
                unique_statements.append(statement)
        return sorted(
            unique_statements,
            key=lambda statement: (statement.startTime, statement.endTime),
        )
