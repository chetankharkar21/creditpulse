import os

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


REQUIRED_SNOWFLAKE_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_ROLE",
]


def _load_private_key(private_key_pem: str) -> bytes:
    """Convert a PEM private key string into Snowflake-compatible DER bytes."""

    # Support secrets that preserve newlines as either real newline
    # characters or escaped "\n" sequences.
    private_key_pem = private_key_pem.replace("\\n", "\n")

    passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
    password = passphrase.encode("utf-8") if passphrase else None

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=password,
    )

    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_snowflake_connection():
    """Create and return a configured Snowflake connection.

    Authentication priority:
    1. Private key supplied directly through an environment variable.
    2. Private key file supplied through an environment variable.
    3. Password authentication.

    This allows CreditPulse engineering workloads to continue using the
    existing password-based configuration while the public Streamlit
    application uses isolated key-pair authentication.
    """

    load_dotenv()

    missing_vars = [
        var for var in REQUIRED_SNOWFLAKE_VARS if not os.getenv(var)
    ]

    if missing_vars:
        raise ValueError(
            "Missing required Snowflake environment variables: "
            + ", ".join(missing_vars)
        )

    connection_params = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }

    private_key_pem = os.getenv("SNOWFLAKE_PRIVATE_KEY")
    private_key_file = os.getenv("SNOWFLAKE_PRIVATE_KEY_FILE")
    password = os.getenv("SNOWFLAKE_PASSWORD")

    if private_key_pem:
        connection_params.update(
            {
                "authenticator": "SNOWFLAKE_JWT",
                "private_key": _load_private_key(private_key_pem),
            }
        )

    elif private_key_file:
        connection_params.update(
            {
                "authenticator": "SNOWFLAKE_JWT",
                "private_key_file": private_key_file,
            }
        )

        private_key_passphrase = os.getenv(
            "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
        )
        if private_key_passphrase:
            connection_params["private_key_file_pwd"] = (
                private_key_passphrase
            )

    elif password:
        connection_params["password"] = password

    else:
        raise ValueError(
            "Snowflake authentication is not configured. Provide one of: "
            "SNOWFLAKE_PRIVATE_KEY, SNOWFLAKE_PRIVATE_KEY_FILE, "
            "or SNOWFLAKE_PASSWORD."
        )

    return snowflake.connector.connect(**connection_params)