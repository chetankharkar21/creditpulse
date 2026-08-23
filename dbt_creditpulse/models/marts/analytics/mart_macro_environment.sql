WITH resolved AS (

    SELECT
        series_id,
        observation_date,
        observation_value
    FROM {{ ref('int_fred_resolved_observations') }}
    WHERE observation_value IS NOT NULL

),

monthly AS (

    SELECT
        observation_date,

        MAX(
            CASE
                WHEN series_id = 'FEDFUNDS'
                THEN observation_value
            END
        ) AS federal_funds_rate,

        MAX(
            CASE
                WHEN series_id = 'UNRATE'
                THEN observation_value
            END
        ) AS unemployment_rate,

        MAX(
            CASE
                WHEN series_id = 'CPIAUCSL'
                THEN observation_value
            END
        ) AS consumer_price_index,

        MAX(
            CASE
                WHEN series_id = 'INDPRO'
                THEN observation_value
            END
        ) AS industrial_production_index

    FROM resolved

    GROUP BY observation_date

),

with_prior_year AS (

    SELECT
        current_month.*,

        prior_year.consumer_price_index
            AS consumer_price_index_prior_year,

        prior_year.industrial_production_index
            AS industrial_production_index_prior_year

    FROM monthly AS current_month

    LEFT JOIN monthly AS prior_year
        ON prior_year.observation_date =
           DATEADD(year, -1, current_month.observation_date)

)

SELECT
    observation_date,

    federal_funds_rate,
    unemployment_rate,

    consumer_price_index,

    CASE
        WHEN consumer_price_index_prior_year IS NOT NULL
             AND consumer_price_index_prior_year <> 0
        THEN (
            consumer_price_index
            / consumer_price_index_prior_year
            - 1
        )
    END AS inflation_yoy_rate,

    industrial_production_index,

    CASE
        WHEN industrial_production_index_prior_year IS NOT NULL
             AND industrial_production_index_prior_year <> 0
        THEN (
            industrial_production_index
            / industrial_production_index_prior_year
            - 1
        )
    END AS industrial_production_yoy_rate

FROM with_prior_year