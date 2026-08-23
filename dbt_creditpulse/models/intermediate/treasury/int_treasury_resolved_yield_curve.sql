WITH ranked AS (

    SELECT
        ingestion_id,
        batch_id,
        observation_date,
        source_period,

        yield_3m_pct,
        yield_2y_pct,
        yield_5y_pct,
        yield_10y_pct,
        yield_30y_pct,

        source_url,
        fetched_at,
        payload_hash,
        raw_record,
        created_at,

        COUNT(*) OVER (
            PARTITION BY observation_date
        ) AS revision_count,

        MIN(fetched_at) OVER (
            PARTITION BY observation_date
        ) AS first_seen_at,

        MAX(fetched_at) OVER (
            PARTITION BY observation_date
        ) AS latest_seen_at,

        ROW_NUMBER() OVER (
            PARTITION BY observation_date
            ORDER BY
                fetched_at DESC,
                created_at DESC,
                ingestion_id DESC
        ) AS revision_rank

    FROM {{ ref('stg_treasury_yield_curve') }}

)

SELECT
    ingestion_id,
    batch_id,
    observation_date,
    source_period,

    yield_3m_pct,
    yield_2y_pct,
    yield_5y_pct,
    yield_10y_pct,
    yield_30y_pct,

    revision_count,
    revision_count > 1 AS has_revision,

    first_seen_at,
    latest_seen_at,

    source_url,
    fetched_at,
    payload_hash,
    raw_record,
    created_at

FROM ranked

WHERE revision_rank = 1