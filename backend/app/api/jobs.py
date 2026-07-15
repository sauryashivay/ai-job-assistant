from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Job
from backend.app.services.ingestion import save_adzuna_jobs

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("/refresh")
def refresh_jobs(
    db: DatabaseSession,
    keyword: str = Query(
        default="software engineer",
        min_length=2,
        max_length=100,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
    ),
) -> dict:
    try:
        result = save_adzuna_jobs(
            db=db,
            keyword=keyword,
            results_per_page=limit,
        )

        return {
            "message": "Jobs refreshed successfully",
            "keyword": keyword,
            **result,
        }

    except (ValueError, RuntimeError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@router.get("")
def get_jobs(
    db: DatabaseSession,
    keyword: str | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> list[dict]:
    statement = (
        select(Job)
        .where(Job.is_active.is_(True))
        .order_by(Job.posted_at.desc())
        .limit(limit)
    )

    if keyword:
        statement = (
            select(Job)
            .where(
                Job.is_active.is_(True),
                Job.title.ilike(f"%{keyword}%"),
            )
            .order_by(Job.posted_at.desc())
            .limit(limit)
        )

    jobs = db.scalars(statement).all()

    return [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "employment_type": job.employment_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "posted_at": job.posted_at,
            "application_url": job.application_url,
            "source": job.source,
        }
        for job in jobs
    ]