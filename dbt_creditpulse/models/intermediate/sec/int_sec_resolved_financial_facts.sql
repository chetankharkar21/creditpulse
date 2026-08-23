with canonical_facts as (

    select *
    from {{ ref('int_sec_canonical_financial_facts') }}

),

ranked_facts as (

    select
        *,

        row_number() over (
            partition by
                cik,
                canonical_metric,
                reporting_period_scope,
                period_start_date,
                period_end_date

            order by
                filed_date desc,
                accession_number desc,
                mapping_priority asc,
                sec_concept asc
        ) as latest_record_rank,

        row_number() over (
            partition by
                cik,
                canonical_metric,
                reporting_period_scope,
                period_start_date,
                period_end_date

            order by
                filed_date asc,
                accession_number asc,
                mapping_priority asc,
                sec_concept asc
        ) as original_record_rank

    from canonical_facts

),

period_history as (

    select
        cik,
        canonical_metric,
        reporting_period_scope,
        period_start_date,
        period_end_date,

        count(*) as observation_count,
        count(distinct accession_number) as filing_count,
        count(distinct metric_value) as distinct_value_count,

        min(filed_date) as first_filed_date,
        max(filed_date) as latest_filed_date,

        case
            when count(distinct metric_value) > 1 then true
            else false
        end as is_revised

    from canonical_facts

    group by
        cik,
        canonical_metric,
        reporting_period_scope,
        period_start_date,
        period_end_date

),

latest_records as (

    select *
    from ranked_facts
    where latest_record_rank = 1

),

original_records as (

    select
        cik,
        canonical_metric,
        reporting_period_scope,
        period_start_date,
        period_end_date,

        metric_value as original_metric_value,
        accession_number as original_accession_number,
        filed_date as original_filed_date

    from ranked_facts

    where original_record_rank = 1

)

select
    latest.ingestion_id,
    latest.batch_id,

    latest.cik,
    latest.entity_name,

    latest.canonical_metric,

    latest.taxonomy,
    latest.sec_concept,
    latest.concept_label,

    latest.unit,

    latest.period_start_date,
    latest.period_end_date,
    latest.period_days,
    latest.reporting_period_scope,

    latest.metric_value,

    original.original_metric_value,

    latest.metric_value - original.original_metric_value
        as revision_amount,

    case
        when original.original_metric_value = 0 then null
        else (
            latest.metric_value - original.original_metric_value
        ) / abs(original.original_metric_value)
    end as revision_pct,

    latest.accession_number,
    latest.fiscal_year,
    latest.fiscal_period,
    latest.filing_form,
    latest.filed_date,
    latest.frame,
    latest.fact_period_type,

    latest.mapping_priority,

    history.observation_count,
    history.filing_count,
    history.distinct_value_count,

    history.first_filed_date,
    history.latest_filed_date,
    history.is_revised,

    original.original_accession_number,
    original.original_filed_date

from latest_records as latest

inner join period_history as history
    on latest.cik = history.cik
    and latest.canonical_metric = history.canonical_metric
    and latest.reporting_period_scope = history.reporting_period_scope
    and latest.period_end_date = history.period_end_date
    and (
        latest.period_start_date = history.period_start_date
        or (
            latest.period_start_date is null
            and history.period_start_date is null
        )
    )

inner join original_records as original
    on latest.cik = original.cik
    and latest.canonical_metric = original.canonical_metric
    and latest.reporting_period_scope = original.reporting_period_scope
    and latest.period_end_date = original.period_end_date
    and (
        latest.period_start_date = original.period_start_date
        or (
            latest.period_start_date is null
            and original.period_start_date is null
        )
    )