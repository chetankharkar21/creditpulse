WITH source AS (

    SELECT *
    FROM {{ source('treasury', 'yield_curve') }}

),

typed AS (

    SELECT
        ingestion_id,
        batch_id,
        observation_date,
        source_period,

        TRY_TO_DECIMAL(
            NULLIF(TRIM(raw_record:"3 Mo"::STRING), ''),
            10,
            4
        ) AS yield_3m_pct,

        TRY_TO_DECIMAL(
            NULLIF(TRIM(raw_record:"2 Yr"::STRING), ''),
            10,
            4
        ) AS yield_2y_pct,

        TRY_TO_DECIMAL(
            NULLIF(TRIM(raw_record:"5 Yr"::STRING), ''),
            10,
            4
        ) AS yield_5y_pct,

        TRY_TO_DECIMAL(
            NULLIF(TRIM(raw_record:"10 Yr"::STRING), ''),
            10,
            4
        ) AS yield_10y_pct,

        TRY_TO_DECIMAL(
            NULLIF(TRIM(raw_record:"30 Yr"::STRING), ''),
            10,
            4
        ) AS yield_30y_pct,

        source_url,
        fetched_at,
        payload_hash,
        raw_record,
        created_at

    FROM source

)

SELECT *
FROM typed