import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api import auth, profile, skills, goals, recommendations, learning_path, progress, chat, assessments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Personalized Learning Path Recommender",
    description="Generates personalized, explainable learning roadmaps using a hybrid "
    "recommendation engine (embeddings + deterministic rules) with Gemini for "
    "natural-language understanding and explanations.",
    version="1.0.0",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# Global error handling: never leak internal errors or API keys
# ---------------------------------------------------------------
@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error on %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "A database error occurred. Please try again shortly."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


# ---------------------------------------------------------------
# Routers
# ---------------------------------------------------------------
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(skills.router)
app.include_router(goals.router)
app.include_router(recommendations.router)
app.include_router(learning_path.router)
app.include_router(progress.router)
app.include_router(chat.router)
app.include_router(assessments.router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.get("/", tags=["health"])
def root():
    return {"message": "Personalized Learning Path Recommender API. See /docs for the API reference."}
