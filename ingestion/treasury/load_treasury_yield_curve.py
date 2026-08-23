import argparse
import csv
import hashlib
import io
import json
import uuid
from datetime import datetime, timezone

from ingestion.common.snowflake_connection import get_snowflake_connection
from ingestion.treasury.treasury_client import get_yield_curve_csv


def load_treasury_yield_curve(source_period: str) -> None:
    """Load one month of Treasury yield-curve observations into RAW."""

    csv_text, source_url = get_yield_curve_csv(source_period)

    reader = csv.DictReader(io.StringIO(csv_text))
    records = list(reader)

    if not records:
        print(f"No Treasury observations returned for {source_period}.")
        return

    fetched_at = datetime.now(timezone.utc)

    batch_id = (
        f"treasury_{source_period}_"
        f"{fetched_at.strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid.uuid4().hex[:8]}"
    )

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                OBSERVATION_DATE,
                PAYLOAD_HASH
            FROM CREDITPULSE.RAW.TREASURY_YIELD_CURVE
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY OBSERVATION_DATE
                ORDER BY FETCHED_AT DESC, CREATED_AT DESC
            ) = 1
            """
        )

        existing_hashes = {
            str(observation_date): payload_hash
            for observation_date, payload_hash in cursor.fetchall()
        }

        rows_to_insert = []

        for record in records:
            raw_date = record.get("Date")

            if not raw_date:
                continue

            observation_date = datetime.strptime(
                raw_date,
                "%m/%d/%Y",
            ).date()

            canonical_json = json.dumps(
                record,
                sort_keys=True,
                separators=(",", ":"),
            )

            payload_hash = hashlib.sha256(
                canonical_json.encode("utf-8")
            ).hexdigest()

            if existing_hashes.get(str(observation_date)) == payload_hash:
                continue

            rows_to_insert.append(
                (
                    str(uuid.uuid4()),
                    batch_id,
                    observation_date,
                    source_period,
                    source_url,
                    fetched_at,
                    payload_hash,
                    canonical_json,
                )
            )

        if not rows_to_insert:
            print("No Treasury changes detected.")
            print(f"Source period:         {source_period}")
            print(f"Fetched observations: {len(records)}")
            return

        for row in rows_to_insert:
            cursor.execute(
                """
                INSERT INTO CREDITPULSE.RAW.TREASURY_YIELD_CURVE (
                    INGESTION_ID,
                    BATCH_ID,
                    OBSERVATION_DATE,
                    SOURCE_PERIOD,
                    SOURCE_URL,
                    FETCHED_AT,
                    PAYLOAD_HASH,
                    RAW_RECORD
                )
                SELECT
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    PARSE_JSON(%s)
                """,
                row,
            )

        connection.commit()

        print("Treasury Bronze load successful.")
        print(f"Source period:          {source_period}")
        print(f"Fetched observations:  {len(records)}")
        print(f"Inserted observations: {len(rows_to_insert)}")
        print(f"Batch ID:               {batch_id}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load Treasury yield-curve observations into CreditPulse RAW."
    )

    parser.add_argument(
        "--source-period",
        required=True,
        help="Treasury source month in YYYYMM format, for example 202608.",
    )

    args = parser.parse_args()

    load_treasury_yield_curve(args.source_period)


if __name__ == "__main__":
    main()