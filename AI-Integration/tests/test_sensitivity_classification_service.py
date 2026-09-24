import pytest

from app.models.schemas import MeetingInformation, MeetingStatement, SensitivityLevel
from app.services.sensitivity_classification_service import SensitivityClassificationService


def make_statement(text: str) -> MeetingStatement:
    return MeetingStatement(
        text=text,
        speaker="SPEAKER_01",
        startTime=10.0,
        endTime=12.5,
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("This update is public.", SensitivityLevel.PUBLIC),
        ("John will prepare the presentation.", SensitivityLevel.INTERNAL),
        ("The team discussed the project budget.", SensitivityLevel.CONFIDENTIAL),
        ("This is confidential.", SensitivityLevel.CONFIDENTIAL),
        ("The API key is abc123.", SensitivityLevel.RESTRICTED),
        ("The approved expansion budget is \u20b950 lakh.", SensitivityLevel.RESTRICTED),
        ("Her phone number is in the file.", SensitivityLevel.CONFIDENTIAL),
        ("The legal case requires review.", SensitivityLevel.CONFIDENTIAL),
        ("The employee complaint is under review.", SensitivityLevel.CONFIDENTIAL),
        ("The acquisition plan is ready.", SensitivityLevel.CONFIDENTIAL),
        ("This is strictly confidential.", SensitivityLevel.RESTRICTED),
        ("This item is restricted and confidential.", SensitivityLevel.RESTRICTED),
        ("", SensitivityLevel.INTERNAL),
        ("The meeting starts at 3 PM.", SensitivityLevel.INTERNAL),
    ],
)
def test_classifies_deterministic_sensitivity_levels(text, expected):
    result = SensitivityClassificationService().classify_statement(make_statement(text))

    assert result.sensitivity == expected


def test_higher_sensitivity_signal_wins_over_lower_explicit_label():
    result = SensitivityClassificationService().classify_statement(
        make_statement("This public note contains an access token.")
    )

    assert result.sensitivity == SensitivityLevel.RESTRICTED


def test_preserves_original_statement_fields():
    statement = make_statement("The contract was approved.")

    result = SensitivityClassificationService().classify_statement(statement)

    assert result.text == statement.text
    assert result.speaker == "SPEAKER_01"
    assert result.startTime == 10.0
    assert result.endTime == 12.5


def test_classifies_extracted_decisions_and_action_items_without_duplicates():
    shared = make_statement("Please rotate the password.")
    later_action = MeetingStatement(
        text="John will prepare the presentation.",
        speaker="SPEAKER_02",
        startTime=20.0,
        endTime=22.0,
    )
    information = MeetingInformation(decisions=[shared], actionItems=[shared, later_action])

    result = SensitivityClassificationService().classify_information(information)

    assert [item.text for item in result] == [
        "Please rotate the password.",
        "John will prepare the presentation.",
    ]
    assert result[0].sensitivity == SensitivityLevel.RESTRICTED
    assert result[1].sensitivity == SensitivityLevel.INTERNAL
