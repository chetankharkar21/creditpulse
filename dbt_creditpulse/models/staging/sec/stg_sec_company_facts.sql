with source as (

    select *
    from {{ source('sec', 'company_facts') }}

),

renamed as (

    select
        ingestion_id,
        batch_id,

        cik,
        entity_name,

        source_url,
        fetched_at,
        payload_hash,

        raw_payload:cik::varchar as payload_cik,
        raw_payload:entityName::varchar as payload_entity_name,

        raw_payload,

        created_at

    from source

)

select *
from renamed