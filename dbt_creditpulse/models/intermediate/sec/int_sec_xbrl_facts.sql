with company_facts as (

    select *
    from {{ ref('stg_sec_company_facts') }}

),

flattened as (

    select
        company_facts.ingestion_id,
        company_facts.batch_id,
        company_facts.cik,
        company_facts.entity_name,
        company_facts.fetched_at,
        company_facts.payload_hash,

        taxonomy.key::varchar as taxonomy,
        concept.key::varchar as concept,

        concept.value:label::varchar as concept_label,
        concept.value:description::varchar as concept_description,

        unit.key::varchar as unit,

        try_to_date(observation.value:start::varchar) as period_start_date,
        try_to_date(observation.value:end::varchar) as period_end_date,

        observation.value:val as fact_value_raw,
        try_to_decimal(
            observation.value:val::varchar,
            38,
            6
        ) as fact_value_numeric,
        observation.value:val::varchar as fact_value_text,

        observation.value:accn::varchar as accession_number,
        try_to_number(observation.value:fy::varchar) as fiscal_year,
        observation.value:fp::varchar as fiscal_period,
        observation.value:form::varchar as filing_form,
        try_to_date(observation.value:filed::varchar) as filed_date,
        observation.value:frame::varchar as frame,

        case
            when observation.value:start is null then 'instant'
            else 'duration'
        end as fact_period_type

    from company_facts,

    lateral flatten(
        input => company_facts.raw_payload:facts
    ) taxonomy,

    lateral flatten(
        input => taxonomy.value
    ) concept,

    lateral flatten(
        input => concept.value:units
    ) unit,

    lateral flatten(
        input => unit.value
    ) observation

)

select *
from flattened