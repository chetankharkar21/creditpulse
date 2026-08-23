WITH ranked AS (

    SELECT
        ingestion_id,
        batch_id,
        series_id,
        observation_date,
        raw_value,
        observation_value,
        realtime_start,
        realtime_end,
        fetched_at,
        source_system,
        raw_record,
        created_at,

        COUNT(*) OVER (
            PARTITION BY series_id, observation_date
        ) AS revision_count,

        MIN(fetched_at) OVER (
            PARTITION BY series_id, observation_date
        ) AS first_seen_at,

        MAX(fetched_at) OVER (
            PARTITION BY series_id, observation_date
        ) AS latest_seen_at,

        ROW_NUMBER() OVER (
            PARTITION BY series_id, observation_date
            ORDER BY
                fetched_at DESC,
                created_at DESC,
                ingestion_id DESC
        ) AS revision_rank

    FROM {{ ref('stg_fred_observations') }}

)

SELECT
    ingestion_id,
    batch_id,
    series_id,
    observation_date,

    raw_value,
    observation_value,

    observation_value IS NULL AS is_missing_value,

    realtime_start,
    realtime_end,

    revision_count,
    revision_count > 1 AS has_revision,

    first_seen_at,
    latest_seen_at,

    fetched_at,
    source_system,
    raw_record,
    created_at

FROM ranked

WHERE revision_rank = 1