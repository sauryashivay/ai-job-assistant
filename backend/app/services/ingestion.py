from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Job
from backend.app.sources.adzuna import fetch_adzuna_jobs


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).replace(tzinfo=None)

    except ValueError:
        return None


def extract_location(job_data: dict[str, Any]) -> str | None:
    location = job_data.get("location", {})

    display_name = location.get("display_name")

    if display_name:
        return display_name

    area = location.get("area", [])

    if area:
        return ", ".join(area)

    return None


def save_adzuna_jobs(
    db: Session,
    keyword: str,
    results_per_page: int = 20,
) -> dict[str, int]:
    jobs = fetch_adzuna_jobs(
        keyword=keyword,
        results_per_page=results_per_page,
    )

    created_count = 0
    updated_count = 0

    for job_data in jobs:
        external_job_id = str(job_data.get("id", ""))

        if not external_job_id:
            continue

        existing_job = db.scalar(
            select(Job).where(
                Job.source == "adzuna",
                Job.external_job_id == external_job_id,
            )
        )

        company_data = job_data.get("company") or {}
        company_name = company_data.get(
            "display_name",
            "Unknown company",
        )

        salary_min = job_data.get("salary_min")
        salary_max = job_data.get("salary_max")

        if existing_job:
            existing_job.title = job_data.get(
                "title",
                "Untitled job",
            )

            existing_job.company = company_name
            existing_job.location = extract_location(job_data)
            existing_job.description = job_data.get("description")
            existing_job.salary_min = salary_min
            existing_job.salary_max = salary_max

            existing_job.application_url = job_data.get(
                "redirect_url",
                "",
            )

            existing_job.posted_at = parse_datetime(
                job_data.get("created")
            )

            existing_job.is_active = True
            existing_job.last_seen_at = datetime.utcnow()

            updated_count += 1

        else:
            new_job = Job(
                external_job_id=external_job_id,
                source="adzuna",
                title=job_data.get("title", "Untitled job"),
                company=company_name,
                location=extract_location(job_data),
                description=job_data.get("description"),
                employment_type=job_data.get("contract_time"),
                salary_min=salary_min,
                salary_max=salary_max,
                application_url=job_data.get("redirect_url", ""),
                posted_at=parse_datetime(job_data.get("created")),
                is_active=True,
            )

            db.add(new_job)
            created_count += 1

    db.commit()

    return {
        "fetched": len(jobs),
        "created": created_count,
        "updated": updated_count,
    }