from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Job
from backend.app.schemas.resume import ResumeProfile
from backend.app.services.job_matcher import calculate_match_score

router = APIRouter(
    prefix="/matcher",
    tags=["Job Matcher"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

# Temporary storage for the latest analyzed resume
latest_resume: ResumeProfile | None = None


@router.post("/resume")
def save_resume(profile: ResumeProfile):
    global latest_resume
    latest_resume = profile

    return {
        "message": "Resume profile saved successfully."
    }


@router.get("/jobs")
def get_matching_jobs(db: DatabaseSession):
    global latest_resume

    if latest_resume is None:
        raise HTTPException(
            status_code=400,
            detail="Analyze a resume first."
        )

    jobs = db.scalars(
        select(Job).where(Job.is_active == True)
    ).all()

    matches = []

    for job in jobs:
        matches.append(
            calculate_match_score(
                latest_resume,
                job
            )
        )

    matches.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return matches[:20]