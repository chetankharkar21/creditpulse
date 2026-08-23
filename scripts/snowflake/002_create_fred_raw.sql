USE ROLE CREDITPULSE_ENGINEER_ROLE;
USE DATABASE CREDITPULSE;
USE WAREHOUSE CREDITPULSE_WH;

CREATE TABLE IF NOT EXISTS RAW.FRED_OBSERVATIONS (
    ingestion_id       VARCHAR NOT NULL,
    batch_id           VARCHAR NOT NULL,

    series_id          VARCHAR NOT NULL,
    observation_date   DATE,
    raw_value          VARCHAR,

    realtime_start     DATE,
    realtime_end       DATE,

    fetched_at         TIMESTAMP_TZ NOT NULL,
    source_system      VARCHAR DEFAULT 'FRED',

    raw_record         VARIANT,

    created_at         TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);