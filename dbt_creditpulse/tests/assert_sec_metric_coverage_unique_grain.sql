SELECT
    cik,
    canonical_metric,
    COUNT(*) AS row_count
FROM {{ ref('int_sec_metric_coverage') }}
GROUP BY
    cik,
    canonical_metric
HAVING COUNT(*) > 1
