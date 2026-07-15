import re
from typing import Any

from backend.app.models import Job
from backend.app.schemas.resume import ResumeProfile


def normalize_skill(skill: str) -> str:
    return re.sub(r"[^a-z0-9+#.]", "", skill.lower())


def find_matched_skills(
    resume_skills: list[str],
    job_description: str,
) -> list[str]:
    description_lower = job_description.lower()

    matched: list[str] = []

    for skill in resume_skills:
        normalized_skill = normalize_skill(skill)

        if not normalized_skill:
            continue

        normalized_description = normalize_skill(description_lower)

        if normalized_skill in normalized_description:
            matched.append(skill)

    return sorted(set(matched))


def calculate_match_score(
    profile: ResumeProfile,
    job: Job,
) -> dict[str, Any]:
    all_resume_skills = list(
        {
            *profile.skills,
            *profile.programming_languages,
            *profile.frameworks,
            *profile.tools,
        }
    )

    job_text = " ".join(
        filter(
            None,
            [
                job.title,
                job.description,
                job.employment_type,
            ],
        )
    )

    matched_skills = find_matched_skills(
        resume_skills=all_resume_skills,
        job_description=job_text,
    )

    missing_skills = [
        skill
        for skill in all_resume_skills
        if skill not in matched_skills
    ]

    if all_resume_skills:
        skill_score = (
            len(matched_skills) / len(all_resume_skills)
        ) * 70
    else:
        skill_score = 0

    role_score = 0

    for role in profile.suggested_roles:
        if role.lower() in job.title.lower():
            role_score = 20
            break

        role_words = role.lower().split()

        if any(word in job.title.lower() for word in role_words):
            role_score = 10
            break

    fresher_score = 0

    fresher_terms = [
        "fresher",
        "entry level",
        "graduate",
        "intern",
        "0-1 years",
        "0 to 1 years",
    ]

    if any(term in job_text.lower() for term in fresher_terms):
        fresher_score = 10

    final_score = round(
        min(skill_score + role_score + fresher_score, 100),
        2,
    )

    return {
        "job_id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "employment_type": job.employment_type,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "application_url": job.application_url,
        "source": job.source,
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_resume_skills": missing_skills,
    }