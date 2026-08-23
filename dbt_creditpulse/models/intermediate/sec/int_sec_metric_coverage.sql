WITH latest_companies AS (

    SELECT
        cik,
        COALESCE(payload_entity_name, entity_name) AS company_name
    FROM {{ ref('stg_sec_company_facts') }}

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY cik
        ORDER BY fetched_at DESC, created_at DESC, ingestion_id DESC
    ) = 1

),

certified_metrics AS (

    SELECT
        canonical_metric,
        metric_category,
        period_type
    FROM {{ ref('sec_v1_certified_metrics') }}

),

coverage AS (

    SELECT
        companies.cik,
        companies.company_name,
        metrics.canonical_metric,
        metrics.metric_category,
        metrics.period_type,

        COUNT(resolved.canonical_metric) AS observation_count,
        MIN(resolved.period_end_date) AS earliest_period,
        MAX(resolved.period_end_date) AS latest_period

    FROM latest_companies AS companies

    CROSS JOIN certified_metrics AS metrics

    LEFT JOIN {{ ref('int_sec_resolved_financial_facts') }} AS resolved
        ON companies.cik = resolved.cik
        AND metrics.canonical_metric = resolved.canonical_metric

    GROUP BY
        companies.cik,
        companies.company_name,
        metrics.canonical_metric,
        metrics.metric_category,
        metrics.period_type

)

SELECT
    cik,
    company_name,
    canonical_metric,
    metric_category,
    period_type,

    observation_count > 0 AS is_present,

    observation_count,
    earliest_period,
    latest_period

FROM coverage
