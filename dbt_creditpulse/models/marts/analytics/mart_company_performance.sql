WITH performance_facts AS (

    SELECT
        fact.company_key,
        company.company_name,
        fact.period_start_date,
        fact.period_end_date,
        fact.reporting_period_scope,
        metric.canonical_metric,
        fact.metric_value

    FROM {{ ref('fact_financial_metric') }} AS fact

    INNER JOIN {{ ref('dim_company') }} AS company
        ON fact.company_key = company.company_key

    INNER JOIN {{ ref('dim_financial_metric') }} AS metric
        ON fact.metric_key = metric.metric_key

    WHERE metric.canonical_metric IN (
        'REVENUE',
        'OPERATING_CASH_FLOW'
    )

),

aligned_periods AS (

    SELECT
        company_key,
        company_name,
        period_start_date,
        period_end_date,
        reporting_period_scope,

        DATEDIFF(
            'day',
            period_start_date,
            period_end_date
        ) AS period_days,

        MAX(
            CASE
                WHEN canonical_metric = 'REVENUE'
                THEN metric_value
            END
        ) AS revenue,

        MAX(
            CASE
                WHEN canonical_metric = 'OPERATING_CASH_FLOW'
                THEN metric_value
            END
        ) AS operating_cash_flow

    FROM performance_facts

    GROUP BY
        company_key,
        company_name,
        period_start_date,
        period_end_date,
        reporting_period_scope

),

complete_periods AS (

    SELECT *
    FROM aligned_periods

    WHERE revenue IS NOT NULL
      AND operating_cash_flow IS NOT NULL

),

prior_year_candidates AS (

    SELECT
        current_period.*,

        prior_period.period_start_date
            AS prior_year_period_start_date,

        prior_period.period_end_date
            AS prior_year_period_end_date,

        prior_period.revenue
            AS prior_year_revenue,

        prior_period.operating_cash_flow
            AS prior_year_operating_cash_flow,

        ROW_NUMBER() OVER (

            PARTITION BY
                current_period.company_key,
                current_period.period_start_date,
                current_period.period_end_date,
                current_period.reporting_period_scope

            ORDER BY
                ABS(
                    DATEDIFF(
                        'day',
                        prior_period.period_end_date,
                        current_period.period_end_date
                    ) - 365
                )

        ) AS prior_match_rank

    FROM complete_periods AS current_period

    LEFT JOIN complete_periods AS prior_period
        ON current_period.company_key = prior_period.company_key

        AND current_period.reporting_period_scope =
            prior_period.reporting_period_scope

        AND DATEDIFF(
            'day',
            prior_period.period_end_date,
            current_period.period_end_date
        ) BETWEEN 350 AND 380

        AND ABS(
            current_period.period_days -
            prior_period.period_days
        ) <= 7

),

matched_periods AS (

    SELECT *
    FROM prior_year_candidates
    WHERE prior_match_rank = 1

)

SELECT
    company_key,
    company_name,

    period_start_date,
    period_end_date,
    reporting_period_scope,

    revenue,
    operating_cash_flow,

    operating_cash_flow / NULLIF(revenue, 0)
        AS operating_cash_flow_margin,

    prior_year_period_start_date,
    prior_year_period_end_date,

    prior_year_revenue,
    prior_year_operating_cash_flow,

    (revenue - prior_year_revenue)
        / NULLIF(ABS(prior_year_revenue), 0)
        AS revenue_yoy_growth,

    (operating_cash_flow - prior_year_operating_cash_flow)
        / NULLIF(ABS(prior_year_operating_cash_flow), 0)
        AS operating_cash_flow_yoy_growth

FROM matched_periods