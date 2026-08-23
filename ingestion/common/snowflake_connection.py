import os

import snowflake.connector
from dotenv import load_dotenv


REQUIRED_SNOWFLAKE_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_ROLE",
]


def get_snowflake_connection():
    """Create and return a configured Snowflake connection."""

    load_dotenv()

    missing_vars = [
        var for var in REQUIRED_SNOWFLAKE_VARS if not os.getenv(var)
    ]

    if missing_vars:
        raise ValueError(
            "Missing required Snowflake environment variables: "
            + ", ".join(missing_vars)
        )

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )