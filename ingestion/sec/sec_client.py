import os

import requests
from dotenv import load_dotenv


SEC_COMPANY_FACTS_URL = (
    "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
)


def get_company_facts(cik: str) -> tuple[dict, str]:
    """Fetch Company Facts data from the SEC EDGAR API."""

    load_dotenv()

    user_agent = os.getenv("SEC_USER_AGENT")

    if not user_agent:
        raise ValueError("SEC_USER_AGENT is missing from environment variables")

    padded_cik = cik.zfill(10)

    url = SEC_COMPANY_FACTS_URL.format(cik=padded_cik)

    headers = {
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip, deflate",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json(), url