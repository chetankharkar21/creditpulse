SELECT
    company_key,
    period_start_date,
    period_end_date,
    reporting_period_scope,
    COUNT(*) AS row_count

FROM {{ ref('mart_company_performance') }}

GROUP BY
    company_key,
    period_start_date,
    period_end_date,
    reporting_period_scope

HAVING COUNT(*) > 1
