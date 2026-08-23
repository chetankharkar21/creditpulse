with canonical_facts as (

    select *
    from {{ ref('int_sec_canonical_financial_facts') }}

),

total_assets as (

    select *
    from canonical_facts
    where canonical_metric = 'TOTAL_ASSETS'
      and fact_period_type = 'instant'

),

total_equity as (

    select *
    from canonical_facts
    where canonical_metric = 'TOTAL_EQUITY'
      and fact_period_type = 'instant'

),

redeemable_nci as (

    select *
    from canonical_facts
    where canonical_metric = 'REDEEMABLE_NCI'
      and fact_period_type = 'instant'

),

reported_total_liabilities as (

    select *
    from canonical_facts
    where canonical_metric = 'TOTAL_LIABILITIES'
      and fact_period_type = 'instant'

),

derived_total_liabilities as (

    select
        assets.ingestion_id,
        assets.batch_id,

        assets.cik,
        assets.entity_name,

        'TOTAL_LIABILITIES' as canonical_metric,

        'creditpulse' as taxonomy,
        'DERIVED_TOTAL_LIABILITIES' as sec_concept,
        'Total Liabilities (Derived)' as concept_label,

        assets.unit,
        assets.period_start_date,
        assets.period_end_date,

        assets.period_days,
        assets.reporting_period_scope,

        (
            assets.metric_value
            - equity.metric_value
            - coalesce(redeemable.metric_value, 0)
        ) as metric_value,

        assets.accession_number,
        assets.fiscal_year,
        assets.fiscal_period,
        assets.filing_form,
        assets.filed_date,
        assets.frame,
        assets.fact_period_type,

        999 as mapping_priority,

        'DERIVED' as metric_origin,

        case
            when redeemable.metric_value is not null
                then 'TOTAL_ASSETS_MINUS_TOTAL_EQUITY_MINUS_REDEEMABLE_NCI'
            else 'TOTAL_ASSETS_MINUS_TOTAL_EQUITY'
        end as derivation_method

    from total_assets as assets

    inner join total_equity as equity
        on assets.ingestion_id = equity.ingestion_id
        and assets.cik = equity.cik
        and assets.accession_number = equity.accession_number
        and assets.period_end_date = equity.period_end_date
        and assets.unit = equity.unit

    left join redeemable_nci as redeemable
        on assets.ingestion_id = redeemable.ingestion_id
        and assets.cik = redeemable.cik
        and assets.accession_number = redeemable.accession_number
        and assets.period_end_date = redeemable.period_end_date
        and assets.unit = redeemable.unit

    left join reported_total_liabilities as reported
        on assets.ingestion_id = reported.ingestion_id
        and assets.cik = reported.cik
        and assets.accession_number = reported.accession_number
        and assets.period_end_date = reported.period_end_date
        and assets.unit = reported.unit

    where reported.accession_number is null

)

select *
from derived_total_liabilities