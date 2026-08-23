import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


TREASURY_CSV_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/"
    "interest-rates/daily-treasury-rates.csv/all/{source_period}"
)


def get_yield_curve_csv(source_period: str) -> tuple[str, str]:
    """Fetch one month of Daily Treasury Par Yield Curve rates."""

    if len(source_period) != 6 or not source_period.isdigit():
        raise ValueError(
            "source_period must be YYYYMM, for example 202608"
        )

    params = {
        "type": "daily_treasury_yield_curve",
        "field_tdr_date_value_month": source_period,
        "page": "",
        "_format": "csv",
    }

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session = requests.Session()
    session.mount(
        "https://",
        HTTPAdapter(max_retries=retry_strategy),
    )

    response = session.get(
        TREASURY_CSV_URL.format(source_period=source_period),
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    if not response.text.strip():
        raise ValueError(
            f"Treasury returned an empty CSV for {source_period}"
        )

    return response.text, response.url