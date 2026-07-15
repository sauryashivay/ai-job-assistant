from fastapi import FastAPI

from backend.app.database import Base, engine
from backend.app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Assistant API",
    description=(
        "Backend API for job aggregation, conversational job search, "
        "and resume-based job recommendations."
    ),
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "AI Job Assistant API is running",
        "status": "success",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "ai-job-assistant",
    }