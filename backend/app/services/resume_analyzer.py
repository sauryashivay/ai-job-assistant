import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from backend.app.schemas.resume import ResumeProfile

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)


SYSTEM_PROMPT = """
You are a resume analysis system for an AI job assistant.

Extract factual information only from the supplied resume.

Rules:
1. Do not invent skills, experience, education or projects.
2. Normalize skill names, for example:
   - "cpp" should become "C++"
   - "sklearn" should become "scikit-learn"
3. Keep technologies concise.
4. If a value is unavailable, use null, 0 or an empty list.
5. Suggested roles must be based only on the candidate's demonstrated
   skills, education, projects and experience.
6. Return valid JSON only.
"""


def build_resume_prompt(resume_text: str) -> str:
    return f"""
Analyze the resume below and return JSON matching this structure:

{{
  "name": null,
  "email": null,
  "phone": null,
  "summary": null,
  "skills": [],
  "programming_languages": [],
  "frameworks": [],
  "tools": [],
  "education": [
    {{
      "degree": null,
      "institution": null,
      "field_of_study": null,
      "graduation_year": null
    }}
  ],
  "projects": [
    {{
      "name": "",
      "description": null,
      "technologies": []
    }}
  ],
  "experience": [
    {{
      "role": null,
      "company": null,
      "duration": null,
      "description": null
    }}
  ],
  "graduation_year": null,
  "years_of_experience": 0,
  "suggested_roles": []
}}

Resume:

--- START OF RESUME ---
{resume_text}
--- END OF RESUME ---
"""


def extract_json_object(content: str) -> dict[str, Any]:
    cleaned_content = content.strip()

    if cleaned_content.startswith("```"):
        cleaned_content = cleaned_content.removeprefix("```json")
        cleaned_content = cleaned_content.removeprefix("```")
        cleaned_content = cleaned_content.removesuffix("```")
        cleaned_content = cleaned_content.strip()

    try:
        parsed_data = json.loads(cleaned_content)
    except json.JSONDecodeError as error:
        start = cleaned_content.find("{")
        end = cleaned_content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "The AI response did not contain valid JSON."
            ) from error

        try:
            parsed_data = json.loads(
                cleaned_content[start : end + 1]
            )
        except json.JSONDecodeError as nested_error:
            raise ValueError(
                "The AI returned malformed resume data."
            ) from nested_error

    if not isinstance(parsed_data, dict):
        raise ValueError(
            "The AI response must be a JSON object."
        )

    return parsed_data


def analyze_resume(resume_text: str) -> ResumeProfile:
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    client = Groq(api_key=GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": build_resume_prompt(
                        resume_text[:30000]
                    ),
                },
            ],
            temperature=0,
            response_format={
                "type": "json_object",
            },
        )
    except Exception as error:
        raise RuntimeError(
            f"Groq resume analysis failed: {error}"
        ) from error

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    extracted_data = extract_json_object(content)

    try:
        return ResumeProfile.model_validate(extracted_data)
    except ValidationError as error:
        raise ValueError(
            f"Invalid resume profile returned by AI: {error}"
        ) from error