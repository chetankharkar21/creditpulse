WITH financial_facts AS (

    SELECT
        fact.company_key,
        company.company_name,
        fact.period_end_date,
        metric.canonical_metric,
        fact.metric_value

    FROM {{ ref('fact_financial_metric') }} AS fact

    INNER JOIN {{ ref('dim_company') }} AS company
        ON fact.company_key = company.company_key

    INNER JOIN {{ ref('dim_financial_metric') }} AS metric
        ON fact.metric_key = metric.metric_key

    WHERE metric.canonical_metric IN (
        'CASH',
        'CURRENT_ASSETS',
        'CURRENT_LIABILITIES',
        'TOTAL_ASSETS'
    )
    AND fact.reporting_period_scope = 'INSTANT'

),

pivoted AS (

    SELECT
        company_key,
        company_name,
        period_end_date,

        MAX(CASE
            WHEN canonical_metric = 'CASH'
            THEN metric_value
        END) AS cash,

        MAX(CASE
            WHEN canonical_metric = 'CURRENT_ASSETS'
            THEN metric_value
        END) AS current_assets,

        MAX(CASE
            WHEN canonical_metric = 'CURRENT_LIABILITIES'
            THEN metric_value
        END) AS current_liabilities,

        MAX(CASE
            WHEN canonical_metric = 'TOTAL_ASSETS'
            THEN metric_value
        END) AS total_assets

    FROM financial_facts

    GROUP BY
        company_key,
        company_name,
        period_end_date

)

SELECT
    company_key,
    company_name,
    period_end_date,

    cash,
    current_assets,
    current_liabilities,
    total_assets,

    current_assets / NULLIF(current_liabilities, 0)
        AS current_ratio,

    cash / NULLIF(current_liabilities, 0)
        AS cash_ratio,

    cash / NULLIF(total_assets, 0)
        AS cash_to_assets_ratio

FROM pivoted

WHERE
    cash IS NOT NULL
    AND current_assets IS NOT NULL
    AND current_liabilities IS NOT NULL
    AND total_assets IS NOT NULL
