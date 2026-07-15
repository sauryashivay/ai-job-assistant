import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def fetch_adzuna_jobs(
    keyword: str = "software engineer",
    country: str = "in",
    page: int = 1,
    results_per_page: int = 20,
) -> list[dict[str, Any]]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise ValueError(
            "ADZUNA_APP_ID and ADZUNA_APP_KEY are missing from the .env file."
        )

    url = f"{BASE_URL}/{country}/search/{page}"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": keyword,
        "content-type": "application/json",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        raise RuntimeError(
            f"Failed to fetch jobs from Adzuna: {error}"
        ) from error

    data = response.json()

    return data.get("results", [])