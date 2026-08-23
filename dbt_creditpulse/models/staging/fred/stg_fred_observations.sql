WITH source AS (

    SELECT *
    FROM {{ source('fred', 'observations') }}

),

typed AS (

    SELECT
        ingestion_id,
        batch_id,

        UPPER(TRIM(series_id)) AS series_id,

        observation_date,

        -- Preserve exactly what FRED supplied.
        raw_value,

        -- FRED uses "." for certain missing observations.
        TRY_TO_DECIMAL(
            NULLIF(TRIM(raw_value), '.'),
            38,
            10
        ) AS observation_value,

        realtime_start,
        realtime_end,
        fetched_at,
        source_system,
        raw_record,
        created_at

    FROM source

)

SELECT *
FROM typed