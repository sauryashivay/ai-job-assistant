from fastapi import FastAPI

from backend.app import models
from backend.app.api.jobs import router as jobs_router
from backend.app.api.resume import router as resume_router
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Assistant API",
    description=(
        "Backend API for live job aggregation, "
        "job search, and resume recommendations."
    ),
    version="0.2.0",
)

app.include_router(jobs_router)
app.include_router(resume_router)


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