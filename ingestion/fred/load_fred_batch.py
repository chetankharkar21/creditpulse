import csv
from pathlib import Path

from ingestion.fred.load_fred_observations import (
    load_fred_observations,
)


SERIES_CONFIG_PATH = (
    Path(__file__).resolve().parent / "fred_series.csv"
)


def load_enabled_series() -> None:
    """Load every enabled governed FRED series."""

    with SERIES_CONFIG_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        series_config = list(reader)

    required_columns = {
        "series_id",
        "metric_name",
        "category",
        "enabled",
    }

    if not series_config:
        raise ValueError("FRED series configuration is empty.")

    if not required_columns.issubset(series_config[0]):
        raise ValueError(
            "FRED series configuration is missing required columns."
        )

    enabled_series = [
        row
        for row in series_config
        if row["enabled"].strip().lower() == "true"
    ]

    if not enabled_series:
        raise ValueError("No FRED series are enabled.")

    series_ids = [
        row["series_id"].strip().upper()
        for row in enabled_series
    ]

    if len(series_ids) != len(set(series_ids)):
        raise ValueError(
            "Duplicate series IDs found in FRED configuration."
        )

    print(
        f"Loading {len(enabled_series)} governed FRED series..."
    )

    for row in enabled_series:
        series_id = row["series_id"].strip().upper()
        metric_name = row["metric_name"].strip()

        print(
            f"\nLoading FRED series "
            f"{series_id} ({metric_name})..."
        )

        load_fred_observations(series_id)


def main():
    load_enabled_series()


if __name__ == "__main__":
    main()