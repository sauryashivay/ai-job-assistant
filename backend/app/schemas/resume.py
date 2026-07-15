from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = None


class ProjectItem(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    role: str | None = None
    company: str | None = None
    duration: str | None = None
    description: str | None = None


class ResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    summary: str | None = None

    skills: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)

    education: list[EducationItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)

    graduation_year: int | None = None
    years_of_experience: float = 0
    suggested_roles: list[str] = Field(default_factory=list)