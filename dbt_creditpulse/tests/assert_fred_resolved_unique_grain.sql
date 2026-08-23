SELECT
    series_id,
    observation_date,
    COUNT(*) AS row_count

FROM {{ ref('int_fred_resolved_observations') }}

GROUP BY
    series_id,
    observation_date

HAVING COUNT(*) > 1