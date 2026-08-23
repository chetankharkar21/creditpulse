SELECT
    observation_date,
    COUNT(*) AS row_count

FROM {{ ref('int_treasury_resolved_yield_curve') }}

GROUP BY observation_date

HAVING COUNT(*) > 1