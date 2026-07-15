from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Job
from backend.app.services.query_parser import parse_query

router = APIRouter(
    prefix="/chat",
    tags=["AI Search"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post("/search")
def search_jobs(
    query: str,
    db: DatabaseSession,
):
    parsed = parse_query(query)

    statement = select(Job)

    keyword = parsed.get("keyword", "").strip()

    if keyword:
        statement = statement.where(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.description.ilike(f"%{keyword}%"),
                Job.company.ilike(f"%{keyword}%"),
                Job.employment_type.ilike(f"%{keyword}%"),
            )
        )

    location = parsed.get("location", "").strip()

    if location:
        statement = statement.where(
            Job.location.ilike(f"%{location}%")
        )

    minimum_salary = parsed.get(
        "minimum_salary",
        0,
    )

    if minimum_salary:
        statement = statement.where(
            Job.salary_max >= minimum_salary
        )

    if parsed.get("remote"):
        statement = statement.where(
            or_(
                Job.location.ilike("%remote%"),
                Job.description.ilike("%remote%"),
            )
        )

    if parsed.get("internship"):
        statement = statement.where(
            or_(
                Job.title.ilike("%intern%"),
                Job.description.ilike("%intern%"),
            )
        )

    jobs = db.scalars(statement).all()

    return {
        "parsed_query": parsed,
        "total_jobs": len(jobs),
        "jobs": jobs,
    }