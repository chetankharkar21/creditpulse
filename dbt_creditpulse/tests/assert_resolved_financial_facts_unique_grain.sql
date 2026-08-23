select
    cik,
    canonical_metric,
    reporting_period_scope,
    period_start_date,
    period_end_date,
    count(*) as row_count

from {{ ref('int_sec_resolved_financial_facts') }}

group by
    cik,
    canonical_metric,
    reporting_period_scope,
    period_start_date,
    period_end_date

having count(*) > 1