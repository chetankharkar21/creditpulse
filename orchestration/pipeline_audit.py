import os
from datetime import datetime, timezone
from uuid import uuid4

from ingestion.common.snowflake_connection import get_snowflake_connection


PIPELINE_NAME = "creditpulse"


def get_execution_metadata() -> dict[str, str | None]:
    """Return execution metadata for local or GitHub Actions runs."""

    is_github_actions = os.getenv("GITHUB_ACTIONS", "").lower() == "true"

    if is_github_actions:
        return {
            "execution_environment": "GITHUB_ACTIONS",
            "trigger_type": os.getenv("GITHUB_EVENT_NAME"),
            "git_sha": os.getenv("GITHUB_SHA"),
            "github_run_id": os.getenv("GITHUB_RUN_ID"),
        }

    return {
        "execution_environment": "LOCAL",
        "trigger_type": "manual_local",
        "git_sha": None,
        "github_run_id": None,
    }


def start_pipeline_run() -> str:
    """Insert a RUNNING audit record and return its run ID."""

    run_id = str(uuid4())
    started_at = datetime.now(timezone.utc)
    metadata = get_execution_metadata()

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO CREDITPULSE.CONTROL.PIPELINE_RUNS (
                    RUN_ID,
                    PIPELINE_NAME,
                    STATUS,
                    STARTED_AT,
                    EXECUTION_ENVIRONMENT,
                    TRIGGER_TYPE,
                    GIT_SHA,
                    GITHUB_RUN_ID
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    PIPELINE_NAME,
                    "RUNNING",
                    started_at,
                    metadata["execution_environment"],
                    metadata["trigger_type"],
                    metadata["git_sha"],
                    metadata["github_run_id"],
                ),
            )

        finally:
            cursor.close()

    finally:
        connection.close()

    return run_id


def finish_pipeline_run(
    run_id: str,
    status: str,
    duration_seconds: float,
    error_message: str | None = None,
) -> None:
    """Mark a pipeline audit record as SUCCESS or FAILED."""

    if status not in {"SUCCESS", "FAILED"}:
        raise ValueError(
            f"Invalid pipeline status: {status}. "
            "Expected SUCCESS or FAILED."
        )

    finished_at = datetime.now(timezone.utc)

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE CREDITPULSE.CONTROL.PIPELINE_RUNS
                SET
                    STATUS = %s,
                    FINISHED_AT = %s,
                    DURATION_SECONDS = %s,
                    ERROR_MESSAGE = %s,
                    UPDATED_AT = CURRENT_TIMESTAMP()
                WHERE RUN_ID = %s
                """,
                (
                    status,
                    finished_at,
                    duration_seconds,
                    error_message,
                    run_id,
                ),
            )

        finally:
            cursor.close()

    finally:
        connection.close()