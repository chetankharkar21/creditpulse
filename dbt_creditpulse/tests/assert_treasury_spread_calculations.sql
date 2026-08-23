SELECT *
FROM {{ ref('mart_treasury_yield_curve') }}

WHERE
    ABS(
        spread_10y_2y_bps
        - ((yield_10y_pct - yield_2y_pct) * 100)
    ) > 0.0001

    OR ABS(
        spread_10y_3m_bps
        - ((yield_10y_pct - yield_3m_pct) * 100)
    ) > 0.0001

    OR is_10y_2y_inverted
        <> ((yield_10y_pct - yield_2y_pct) < 0)

    OR is_10y_3m_inverted
        <> ((yield_10y_pct - yield_3m_pct) < 0)