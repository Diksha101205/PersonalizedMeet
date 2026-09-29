import pytest

from app.models.schemas import ClassifiedInformationItem, ParticipantRole, SensitivityLevel
from app.services.authorization_service import AuthorizationService
from app.utils.errors import InvalidParticipantRoleError


def classified_item(sensitivity: SensitivityLevel) -> ClassifiedInformationItem:
    return ClassifiedInformationItem(
        text=f"{sensitivity.value} information",
        speaker="SPEAKER_01",
        startTime=10.0,
        endTime=12.5,
        sensitivity=sensitivity,
    )


ALL_ITEMS = [classified_item(level) for level in SensitivityLevel]


@pytest.mark.parametrize(
    "role",
    [ParticipantRole.HOST, ParticipantRole.ORGANIZER, ParticipantRole.SENIOR],
)
def test_full_access_roles_can_access_every_sensitivity_level(role):
    result = AuthorizationService().filter_information(role, ALL_ITEMS)

    assert result.authorizedInformation == ALL_ITEMS
    assert result.filteredInformation == []


def test_manager_cannot_access_restricted_information():
    result = AuthorizationService().filter_information(ParticipantRole.MANAGER, ALL_ITEMS)

    assert [item.sensitivity for item in result.authorizedInformation] == [
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
        SensitivityLevel.CONFIDENTIAL,
    ]
    assert [item.sensitivity for item in result.filteredInformation] == [SensitivityLevel.RESTRICTED]


def test_participant_cannot_access_confidential_or_restricted_information():
    result = AuthorizationService().filter_information(ParticipantRole.PARTICIPANT, ALL_ITEMS)

    assert [item.sensitivity for item in result.authorizedInformation] == [
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
    ]
    assert [item.sensitivity for item in result.filteredInformation] == [
        SensitivityLevel.CONFIDENTIAL,
        SensitivityLevel.RESTRICTED,
    ]


@pytest.mark.parametrize("role", list(ParticipantRole))
def test_public_and_internal_information_are_accessible_to_every_role(role):
    result = AuthorizationService().filter_information(
        role,
        [classified_item(SensitivityLevel.PUBLIC), classified_item(SensitivityLevel.INTERNAL)],
    )

    assert [item.sensitivity for item in result.authorizedInformation] == [
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
    ]
    assert result.filteredInformation == []


def test_empty_classified_information_returns_empty_collections():
    result = AuthorizationService().filter_information(ParticipantRole.PARTICIPANT, [])

    assert result.authorizedInformation == []
    assert result.filteredInformation == []


def test_mixed_information_is_partitioned_without_overlapping_collections():
    result = AuthorizationService().filter_information(ParticipantRole.PARTICIPANT, ALL_ITEMS)

    authorized_ids = {id(item) for item in result.authorizedInformation}
    filtered_ids = {id(item) for item in result.filteredInformation}
    assert authorized_ids.isdisjoint(filtered_ids)
    assert len(result.authorizedInformation) + len(result.filteredInformation) == len(ALL_ITEMS)


def test_authorization_preserves_information_fields():
    item = ClassifiedInformationItem(
        text="The contract was approved.",
        speaker="SPEAKER_02",
        startTime=20.0,
        endTime=25.0,
        sensitivity=SensitivityLevel.CONFIDENTIAL,
    )

    result = AuthorizationService().filter_information(ParticipantRole.MANAGER, [item])

    assert result.authorizedInformation[0] == item


def test_unsupported_role_is_rejected_without_exposing_internal_details():
    with pytest.raises(InvalidParticipantRoleError, match="Unsupported participant role"):
        AuthorizationService().filter_information("GUEST", ALL_ITEMS)
