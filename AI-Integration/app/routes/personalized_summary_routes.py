from fastapi import APIRouter

from app.models.schemas import PersonalizedSummaryRequest, PersonalizedSummaryResponse
from app.services.personalized_summary_service import PersonalizedSummaryService

router = APIRouter(prefix="/api", tags=["personalized-summary"])

personalized_summary_service = PersonalizedSummaryService()


@router.post(
    "/generate-personalized-summary",
    response_model=PersonalizedSummaryResponse,
)
def generate_personalized_summary(
    request: PersonalizedSummaryRequest,
) -> PersonalizedSummaryResponse:
    return personalized_summary_service.generate_summary(request)
