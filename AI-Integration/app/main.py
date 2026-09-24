from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes.processing_routes import router as processing_router
from app.utils.errors import AiProcessingError

app = FastAPI(title=settings.app_name)


@app.exception_handler(AiProcessingError)
async def ai_processing_error_handler(request: Request, exc: AiProcessingError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Unexpected AI service error"},
    )


@app.get("/api/health")
def health_check():
    return {"status": "UP", "message": "PersonalizedMeet AI service is running"}


app.include_router(processing_router)
