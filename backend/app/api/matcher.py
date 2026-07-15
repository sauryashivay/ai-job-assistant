from typing import Annotated, Any

from fastapi import APIRouter, Depends
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


@router.post("/jobs")
def get_matching_jobs(
    profile: ResumeProfile,
    db: DatabaseSession,
) -> list[dict[str, Any]]:
    jobs = db.scalars(
        select(Job).where(Job.is_active.is_(True))
    ).all()

    matches = [
        calculate_match_score(
            profile=profile,
            job=job,
        )
        for job in jobs
    ]

    matches.sort(
        key=lambda match: match["match_score"],
        reverse=True,
    )

    return matches[:20]