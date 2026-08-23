SELECT
    SHA2(canonical_metric, 256) AS metric_key,
    canonical_metric,
    metric_category,
    period_type,
    description

FROM {{ ref('sec_v1_certified_metrics') }}
