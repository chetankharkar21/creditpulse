import shutil
import subprocess
import time
from datetime import datetime, timezone

from ingestion.fred.load_fred_batch import load_enabled_series
from ingestion.sec.load_company_facts_batch import load_enabled_companies
from ingestion.treasury.load_treasury_yield_curve import (
    load_treasury_yield_curve,
)


def current_and_previous_months() -> list[str]:
    """Return previous and current UTC months as YYYYMM."""

    now = datetime.now(timezone.utc)

    current_period = now.strftime("%Y%m")

    if now.month == 1:
        previous_period = f"{now.year - 1}12"
    else:
        previous_period = f"{now.year}{now.month - 1:02d}"

    return [previous_period, current_period]


def run_dbt_build() -> None:
    """Run the complete CreditPulse dbt build."""

    dbt_executable = shutil.which("dbt")

    if not dbt_executable:
        raise RuntimeError(
            "dbt executable was not found in the active environment."
        )

    command = [
        dbt_executable,
        "build",
        "--project-dir",
        "dbt_creditpulse",
        "--profiles-dir",
        "dbt_creditpulse",
    ]

    subprocess.run(
        command,
        check=True,
    )


def run_pipeline() -> None:
    """Run the complete CreditPulse ingestion and transformation pipeline."""

    pipeline_started_at = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    print("=" * 70)
    print("CREDITPULSE PIPELINE START")
    print(f"Started at: {pipeline_started_at.isoformat()}")
    print("=" * 70)

    print("\n[1/4] SEC ingestion")
    load_enabled_companies()

    print("\n[2/4] FRED ingestion")
    load_enabled_series()

    print("\n[3/4] U.S. Treasury ingestion")

    for source_period in current_and_previous_months():
        print(f"\nLoading Treasury period {source_period}...")
        load_treasury_yield_curve(source_period)

    print("\n[4/4] dbt build")
    run_dbt_build()

    elapsed_seconds = time.perf_counter() - start_time

    print("\n" + "=" * 70)
    print("CREDITPULSE PIPELINE SUCCESS")
    print(f"Elapsed seconds: {elapsed_seconds:.2f}")
    print("=" * 70)


def main():
    try:
        run_pipeline()

    except Exception as exc:
        print("\n" + "=" * 70)
        print("CREDITPULSE PIPELINE FAILED")
        print(f"Error: {exc}")
        print("=" * 70)

        raise


if __name__ == "__main__":
    main()