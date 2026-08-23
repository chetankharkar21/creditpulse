USE ROLE CREDITPULSE_ENGINEER_ROLE;
USE DATABASE CREDITPULSE;
USE WAREHOUSE CREDITPULSE_WH;

CREATE TABLE IF NOT EXISTS RAW.TREASURY_YIELD_CURVE (
    ingestion_id       VARCHAR NOT NULL,
    batch_id           VARCHAR NOT NULL,

    observation_date   DATE NOT NULL,
    source_period      VARCHAR NOT NULL,

    source_url         VARCHAR NOT NULL,
    fetched_at         TIMESTAMP_TZ NOT NULL,

    payload_hash       VARCHAR NOT NULL,
    raw_record         VARIANT NOT NULL,

    created_at         TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);