import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone

from ingestion.common.snowflake_connection import get_snowflake_connection
from ingestion.sec.sec_client import get_company_facts


def generate_payload_hash(payload: dict) -> tuple[str, str]:
    """Return canonical JSON and its SHA-256 hash."""

    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    payload_hash = hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

    return canonical_json, payload_hash


def load_company_facts(cik: str) -> None:
    """Fetch SEC Company Facts and load a new payload into Snowflake RAW."""

    payload, source_url = get_company_facts(cik)

    canonical_json, payload_hash = generate_payload_hash(payload)

    fetched_at = datetime.now(timezone.utc)

    ingestion_id = str(uuid.uuid4())

    batch_id = (
        f"sec_company_facts_"
        f"{fetched_at.strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid.uuid4().hex[:8]}"
    )

    source_cik = str(payload.get("cik", cik)).zfill(10)
    entity_name = payload.get("entityName")

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        # Idempotency check:
        # do not reload an identical SEC payload for the same company.
        cursor.execute(
            """
            SELECT 1
            FROM CREDITPULSE.RAW.SEC_COMPANY_FACTS
            WHERE CIK = %s
              AND PAYLOAD_HASH = %s
            LIMIT 1
            """,
            (
                source_cik,
                payload_hash,
            ),
        )

        existing_record = cursor.fetchone()

        if existing_record:
            print("No SEC changes detected.")
            print(f"Company: {entity_name}")
            print(f"CIK:     {source_cik}")
            print("Identical payload already exists in RAW.")
            return

        cursor.execute(
            """
            INSERT INTO CREDITPULSE.RAW.SEC_COMPANY_FACTS (
                INGESTION_ID,
                BATCH_ID,
                CIK,
                ENTITY_NAME,
                SOURCE_URL,
                FETCHED_AT,
                PAYLOAD_HASH,
                RAW_PAYLOAD
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
            (
                ingestion_id,
                batch_id,
                source_cik,
                entity_name,
                source_url,
                fetched_at,
                payload_hash,
                canonical_json,
            ),
        )

        connection.commit()

        print("SEC Company Facts load successful.")
        print(f"Company:      {entity_name}")
        print(f"CIK:          {source_cik}")
        print(f"Ingestion ID: {ingestion_id}")
        print(f"Batch ID:     {batch_id}")
        print(f"Payload hash: {payload_hash}")

    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load SEC Company Facts into CreditPulse RAW."
    )

    parser.add_argument(
        "--cik",
        default="0000320193",
        help="SEC Central Index Key (CIK).",
    )

    args = parser.parse_args()

    load_company_facts(args.cik)


if __name__ == "__main__":
    main()