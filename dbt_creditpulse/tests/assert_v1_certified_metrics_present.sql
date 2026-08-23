SELECT *
FROM {{ ref('int_sec_metric_coverage') }}
WHERE is_present = FALSE
