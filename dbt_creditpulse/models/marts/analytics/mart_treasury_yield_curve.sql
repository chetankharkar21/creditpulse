WITH resolved AS (

    SELECT
        observation_date,

        yield_3m_pct,
        yield_2y_pct,
        yield_5y_pct,
        yield_10y_pct,
        yield_30y_pct

    FROM {{ ref('int_treasury_resolved_yield_curve') }}

)

SELECT
    observation_date,

    yield_3m_pct,
    yield_2y_pct,
    yield_5y_pct,
    yield_10y_pct,
    yield_30y_pct,

    yield_10y_pct - yield_2y_pct
        AS spread_10y_2y_pct_points,

    (yield_10y_pct - yield_2y_pct) * 100
        AS spread_10y_2y_bps,

    yield_10y_pct - yield_3m_pct
        AS spread_10y_3m_pct_points,

    (yield_10y_pct - yield_3m_pct) * 100
        AS spread_10y_3m_bps,

    (yield_10y_pct - yield_2y_pct) < 0
        AS is_10y_2y_inverted,

    (yield_10y_pct - yield_3m_pct) < 0
        AS is_10y_3m_inverted

FROM resolved