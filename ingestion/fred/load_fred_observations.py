import argparse
import uuid
from datetime import datetime, timezone

from ingestion.common.snowflake_connection import get_snowflake_connection
from ingestion.fred.fred_client import get_series_observations


def load_fred_observations(series_id: str) -> None:
    """Fetch one FRED series and load new or revised observations into RAW."""

    payload, _ = get_series_observations(series_id)

    observations = payload.get("observations", [])

    if not observations:
        print(f"No observations returned for {series_id}.")
        return

    fetched_at = datetime.now(timezone.utc)

    batch_id = (
        f"fred_{series_id.lower()}_"
        f"{fetched_at.strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid.uuid4().hex[:8]}"
    )

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        # Get the latest stored value for every observation date.
        # Unchanged observations are skipped.
        # Revised historical values are inserted as new RAW records.
        cursor.execute(
            """
            SELECT
                OBSERVATION_DATE,
                RAW_VALUE
            FROM CREDITPULSE.RAW.FRED_OBSERVATIONS
            WHERE SERIES_ID = %s
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY OBSERVATION_DATE
                ORDER BY FETCHED_AT DESC, CREATED_AT DESC
            ) = 1
            """,
            (series_id,),
        )

        existing_values = {
            str(observation_date): raw_value
            for observation_date, raw_value in cursor.fetchall()
        }

        rows_to_insert = []

        for observation in observations:
            observation_date = observation["date"]
            raw_value = observation["value"]

            if existing_values.get(observation_date) == raw_value:
                continue

            rows_to_insert.append(
                (
                    str(uuid.uuid4()),
                    batch_id,
                    series_id,
                    observation_date,
                    raw_value,
                    observation.get("realtime_start"),
                    observation.get("realtime_end"),
                    fetched_at,
                    "FRED",
                )
            )

        if not rows_to_insert:
            print("No FRED changes detected.")
            print(f"Series:               {series_id}")
            print(f"Fetched observations: {len(observations)}")
            return

        cursor.executemany(
            """
            INSERT INTO CREDITPULSE.RAW.FRED_OBSERVATIONS (
                INGESTION_ID,
                BATCH_ID,
                SERIES_ID,
                OBSERVATION_DATE,
                RAW_VALUE,
                REALTIME_START,
                REALTIME_END,
                FETCHED_AT,
                SOURCE_SYSTEM
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            rows_to_insert,
        )

        # Build the preserved raw observation as VARIANT after the batch insert.
        cursor.execute(
            """
            UPDATE CREDITPULSE.RAW.FRED_OBSERVATIONS
            SET RAW_RECORD = OBJECT_CONSTRUCT(
                'realtime_start', TO_VARCHAR(REALTIME_START, 'YYYY-MM-DD'),
                'realtime_end', TO_VARCHAR(REALTIME_END, 'YYYY-MM-DD'),
                'date', TO_VARCHAR(OBSERVATION_DATE, 'YYYY-MM-DD'),
                'value', RAW_VALUE
            )
            WHERE BATCH_ID = %s
            """,
            (batch_id,),
        )

        connection.commit()

        print("FRED Bronze load successful.")
        print(f"Series:                {series_id}")
        print(f"Fetched observations:  {len(observations)}")
        print(f"Inserted observations: {len(rows_to_insert)}")
        print(f"Batch ID:              {batch_id}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load FRED observations into CreditPulse RAW."
    )

    parser.add_argument(
        "--series-id",
        default="FEDFUNDS",
        help="FRED series identifier.",
    )

    args = parser.parse_args()

    load_fred_observations(args.series_id)


if __name__ == "__main__":
    main()