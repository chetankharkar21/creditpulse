WITH company_history AS (

    SELECT
        cik,
        COALESCE(payload_entity_name, entity_name) AS company_name,
        fetched_at,
        created_at,
        ingestion_id
    FROM {{ ref('stg_sec_company_facts') }}

),

latest_company AS (

    SELECT
        cik,
        company_name,
        fetched_at AS latest_sec_fetch_at

    FROM company_history

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY cik
        ORDER BY fetched_at DESC, created_at DESC, ingestion_id DESC
    ) = 1

),

company_summary AS (

    SELECT
        cik,
        MIN(fetched_at) AS first_sec_fetch_at,
        MAX(fetched_at) AS latest_sec_fetch_at,
        COUNT(*) AS ingestion_count
    FROM company_history
    GROUP BY cik

)

SELECT
    SHA2(latest_company.cik, 256) AS company_key,
    latest_company.cik,
    latest_company.company_name,
    company_summary.first_sec_fetch_at,
    company_summary.latest_sec_fetch_at,
    company_summary.ingestion_count

FROM latest_company

INNER JOIN company_summary
    ON latest_company.cik = company_summary.cik
