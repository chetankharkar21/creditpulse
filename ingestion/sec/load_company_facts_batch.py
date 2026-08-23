import csv
from pathlib import Path

from ingestion.sec.load_company_facts import load_company_facts


COMPANY_CONFIG_PATH = (
    Path(__file__).resolve().parent / "sec_companies.csv"
)


def load_enabled_companies() -> None:
    """Load SEC Company Facts for every enabled governed company."""

    with COMPANY_CONFIG_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        companies = list(reader)

    required_columns = {
        "cik",
        "ticker",
        "company_name",
        "enabled",
    }

    if not companies:
        raise ValueError("SEC company configuration is empty.")

    if not required_columns.issubset(companies[0]):
        raise ValueError(
            "SEC company configuration is missing required columns."
        )

    enabled_companies = [
        company
        for company in companies
        if company["enabled"].strip().lower() == "true"
    ]

    if not enabled_companies:
        raise ValueError("No SEC companies are enabled.")

    ciks = [
        company["cik"].strip().zfill(10)
        for company in enabled_companies
    ]

    if len(ciks) != len(set(ciks)):
        raise ValueError(
            "Duplicate CIK values found in SEC company configuration."
        )

    print(
        f"Loading {len(enabled_companies)} governed SEC companies..."
    )

    for company in enabled_companies:
        cik = company["cik"].strip().zfill(10)
        ticker = company["ticker"].strip()

        print(f"\nLoading SEC company {ticker} ({cik})...")

        load_company_facts(cik)


def main():
    load_enabled_companies()


if __name__ == "__main__":
    main()