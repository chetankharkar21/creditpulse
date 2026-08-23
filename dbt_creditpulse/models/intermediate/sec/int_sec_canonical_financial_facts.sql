with latest_ingestion as (

    select
        ingestion_id,
        cik

    from {{ ref('stg_sec_company_facts') }}

    qualify row_number() over (
        partition by cik
        order by fetched_at desc, created_at desc, ingestion_id desc
    ) = 1

),

xbrl_facts as (

    select
        facts.*

    from {{ ref('int_sec_xbrl_facts') }} as facts

    inner join latest_ingestion
        on facts.ingestion_id = latest_ingestion.ingestion_id

),

metric_mapping as (

    select
        taxonomy,
        sec_concept,
        canonical_metric,
        expected_period_type,
        expected_unit,
        priority

    from {{ ref('sec_metric_mapping') }}

),

mapped_facts as (

    select
        facts.ingestion_id,
        facts.batch_id,

        facts.cik,
        facts.entity_name,

        mapping.canonical_metric,

        facts.taxonomy,
        facts.concept as sec_concept,
        facts.concept_label,

        facts.unit,
        facts.period_start_date,
        facts.period_end_date,

        facts.fact_value_numeric as metric_value,

        facts.accession_number,
        facts.fiscal_year,
        facts.fiscal_period,
        facts.filing_form,
        facts.filed_date,
        facts.frame,
        facts.fact_period_type,

        mapping.priority as mapping_priority,

        row_number() over (
            partition by
                facts.cik,
                mapping.canonical_metric,
                facts.accession_number,
                facts.period_start_date,
                facts.period_end_date,
                facts.unit

            order by
                mapping.priority asc,
                facts.concept asc
        ) as mapping_rank

    from xbrl_facts as facts

    inner join metric_mapping as mapping
        on facts.taxonomy = mapping.taxonomy
        and facts.concept = mapping.sec_concept
        and facts.fact_period_type = mapping.expected_period_type
        and facts.unit = mapping.expected_unit

    where facts.fact_value_numeric is not null

),

classified_facts as (

    select
        *,

        case
            when fact_period_type = 'duration'
                then datediff(
                    'day',
                    period_start_date,
                    period_end_date
                ) + 1
            else null
        end as period_days,

        case
            when fact_period_type = 'instant'
                then 'INSTANT'

            when datediff(
                'day',
                period_start_date,
                period_end_date
            ) + 1 between 80 and 100
                then 'QUARTER'

            when datediff(
                'day',
                period_start_date,
                period_end_date
            ) + 1 between 170 and 200
                then 'YTD_6_MONTHS'

            when datediff(
                'day',
                period_start_date,
                period_end_date
            ) + 1 between 250 and 290
                then 'YTD_9_MONTHS'

            when datediff(
                'day',
                period_start_date,
                period_end_date
            ) + 1 between 350 and 380
                then 'ANNUAL'

            else 'OTHER'
        end as reporting_period_scope

    from mapped_facts

    where mapping_rank = 1

)

select
    ingestion_id,
    batch_id,

    cik,
    entity_name,

    canonical_metric,

    taxonomy,
    sec_concept,
    concept_label,

    unit,
    period_start_date,
    period_end_date,

    period_days,
    reporting_period_scope,

    metric_value,

    accession_number,
    fiscal_year,
    fiscal_period,
    filing_form,
    filed_date,
    frame,
    fact_period_type,

    mapping_priority

from classified_facts