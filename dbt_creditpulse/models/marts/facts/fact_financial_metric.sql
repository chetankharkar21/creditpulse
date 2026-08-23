WITH resolved_facts AS (

    SELECT *
    FROM {{ ref('int_sec_resolved_financial_facts') }}

),

final AS (

    SELECT
        SHA2(
            CONCAT_WS(
                '|',
                company.company_key,
                metric.metric_key,
                facts.reporting_period_scope,
                COALESCE(TO_VARCHAR(facts.period_start_date), 'NULL'),
                TO_VARCHAR(facts.period_end_date)
            ),
            256
        ) AS financial_fact_key,

        company.company_key,
        metric.metric_key,

        facts.period_start_date,
        facts.period_end_date,
        facts.period_days,
        facts.reporting_period_scope,
        facts.fact_period_type,

        facts.metric_value,
        facts.unit,

        facts.fiscal_year,
        facts.fiscal_period,

        facts.filing_form,
        facts.filed_date,
        facts.accession_number,

        facts.is_revised,
        facts.original_metric_value,
        facts.revision_amount,
        facts.revision_pct,

        facts.observation_count,
        facts.filing_count,
        facts.distinct_value_count,
        facts.first_filed_date,
        facts.latest_filed_date,

        facts.ingestion_id,
        facts.batch_id

    FROM resolved_facts AS facts

    INNER JOIN {{ ref('dim_company') }} AS company
        ON facts.cik = company.cik

    INNER JOIN {{ ref('dim_financial_metric') }} AS metric
        ON facts.canonical_metric = metric.canonical_metric

)

SELECT *
FROM final
