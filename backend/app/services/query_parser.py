import json
import os

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)


SYSTEM_PROMPT = """
You are an AI job search assistant.

Extract the user's search intent.

Return ONLY valid JSON.

Schema:

{
    "keyword": "",
    "location": "",
    "minimum_salary": 0,
    "internship": false,
    "remote": false,
    "fresher": false,
    "skills": []
}
"""


def parse_query(query: str) -> dict:

    response = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    return json.loads(
        response.choices[0].message.content
    )