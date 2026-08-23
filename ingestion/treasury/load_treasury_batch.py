import argparse
from datetime import datetime

from ingestion.treasury.load_treasury_yield_curve import (
    load_treasury_yield_curve,
)


def iter_months(start_period: str, end_period: str):
    """Yield YYYYMM values inclusively between two periods."""

    start = datetime.strptime(start_period, "%Y%m")
    end = datetime.strptime(end_period, "%Y%m")

    if start > end:
        raise ValueError("start_period cannot be after end_period")

    current = start

    while current <= end:
        yield current.strftime("%Y%m")

        if current.month == 12:
            current = current.replace(
                year=current.year + 1,
                month=1,
            )
        else:
            current = current.replace(
                month=current.month + 1,
            )


def main():
    parser = argparse.ArgumentParser(
        description="Backfill Treasury yield-curve data by month."
    )

    parser.add_argument(
        "--start-period",
        required=True,
        help="First month in YYYYMM format.",
    )

    parser.add_argument(
        "--end-period",
        required=True,
        help="Last month in YYYYMM format.",
    )

    args = parser.parse_args()

    for source_period in iter_months(
        args.start_period,
        args.end_period,
    ):
        print(f"\nLoading Treasury period {source_period}...")
        load_treasury_yield_curve(source_period)


if __name__ == "__main__":
    main()