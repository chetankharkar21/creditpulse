SELECT
    company_key,
    period_end_date,
    COUNT(*) AS row_count

FROM {{ ref('mart_company_liquidity') }}

GROUP BY
    company_key,
    period_end_date

HAVING COUNT(*) > 1
