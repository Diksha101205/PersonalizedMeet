from app.models.schemas import (
    AuthorizationResult,
    ClassifiedInformationItem,
    ParticipantRole,
    SensitivityLevel,
)
from app.utils.errors import InvalidParticipantRoleError


class AuthorizationService:
    """Filter classified information using the project role-to-sensitivity policy."""

    _ACCESS_POLICY: dict[ParticipantRole, frozenset[SensitivityLevel]] = {
        ParticipantRole.HOST: frozenset(SensitivityLevel),
        ParticipantRole.ORGANIZER: frozenset(SensitivityLevel),
        ParticipantRole.SENIOR: frozenset(SensitivityLevel),
        ParticipantRole.MANAGER: frozenset({
            SensitivityLevel.PUBLIC,
            SensitivityLevel.INTERNAL,
            SensitivityLevel.CONFIDENTIAL,
        }),
        ParticipantRole.PARTICIPANT: frozenset({
            SensitivityLevel.PUBLIC,
            SensitivityLevel.INTERNAL,
        }),
    }

    def filter_information(
        self,
        participant_role: ParticipantRole | str,
        classified_information: list[ClassifiedInformationItem],
    ) -> AuthorizationResult:
        role = self._normalize_role(participant_role)
        permitted_levels = self._ACCESS_POLICY[role]
        authorized_information = [
            item for item in classified_information if item.sensitivity in permitted_levels
        ]
        filtered_information = [
            item for item in classified_information if item.sensitivity not in permitted_levels
        ]
        return AuthorizationResult(
            participantRole=role,
            authorizedInformation=authorized_information,
            filteredInformation=filtered_information,
        )

    def _normalize_role(self, participant_role: ParticipantRole | str) -> ParticipantRole:
        if isinstance(participant_role, ParticipantRole):
            return participant_role
        try:
            return ParticipantRole(participant_role.upper())
        except (AttributeError, ValueError) as exc:
            raise InvalidParticipantRoleError("Unsupported participant role") from exc
