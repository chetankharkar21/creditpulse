import os

import requests
from dotenv import load_dotenv


FRED_SERIES_OBSERVATIONS_URL = (
    "https://api.stlouisfed.org/fred/series/observations"
)


def get_series_observations(series_id: str) -> tuple[dict, str]:
    """Fetch observations for one FRED economic series."""

    load_dotenv()

    api_key = os.getenv("FRED_API_KEY")

    if not api_key:
        raise ValueError("FRED_API_KEY is missing from environment variables")

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }

    response = requests.get(
        FRED_SERIES_OBSERVATIONS_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json(), response.url