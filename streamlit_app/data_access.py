from decimal import Decimal

import pandas as pd

from ingestion.common.snowflake_connection import (
    get_snowflake_connection,
)


def normalize_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert Snowflake numeric Decimal values to native floats.

    Snowflake NUMBER columns may be returned as Decimal objects.
    Converting them centrally keeps Streamlit and Plotly chart
    behavior consistent without changing identifier/date columns.
    """

    dataframe = dataframe.copy()

    for column in dataframe.columns:
        non_null_values = dataframe[column].dropna()

        if non_null_values.empty:
            continue

        first_value = non_null_values.iloc[0]

        if isinstance(first_value, Decimal):
            dataframe[column] = dataframe[column].astype(float)

    return dataframe


def query_dataframe(
    query: str,
    params: tuple | None = None,
) -> pd.DataFrame:
    """Execute a Snowflake query and return a normalized DataFrame."""

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(
                query,
                params or (),
            )

            rows = cursor.fetchall()

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

            dataframe = pd.DataFrame(
                rows,
                columns=columns,
            )

            return normalize_dataframe(
                dataframe
            )

        finally:
            cursor.close()

    finally:
        connection.close()


def get_companies() -> pd.DataFrame:
    """Return the governed company dimension."""

    return query_dataframe(
        """
        SELECT
            company_key,
            cik,
            company_name
        FROM CREDITPULSE.ANALYTICS.DIM_COMPANY
        ORDER BY company_name
        """
    )


def get_liquidity_history(
    company_key: str,
) -> pd.DataFrame:
    """Return historical liquidity metrics for one company."""

    return query_dataframe(
        """
        SELECT
            company_key,
            company_name,
            period_end_date,
            cash,
            current_assets,
            current_liabilities,
            total_assets,
            current_ratio,
            cash_ratio,
            cash_to_assets_ratio
        FROM CREDITPULSE.ANALYTICS.MART_COMPANY_LIQUIDITY
        WHERE company_key = %s
        ORDER BY period_end_date
        """,
        (company_key,),
    )


def get_performance_history(
    company_key: str,
    reporting_period_scope: str = "ANNUAL",
) -> pd.DataFrame:
    """Return aligned company performance history."""

    return query_dataframe(
        """
        SELECT
            company_key,
            company_name,
            period_start_date,
            period_end_date,
            reporting_period_scope,
            revenue,
            operating_cash_flow,
            operating_cash_flow_margin,
            prior_year_revenue,
            prior_year_operating_cash_flow,
            revenue_yoy_growth,
            operating_cash_flow_yoy_growth
        FROM CREDITPULSE.ANALYTICS.MART_COMPANY_PERFORMANCE
        WHERE company_key = %s
          AND reporting_period_scope = %s
        ORDER BY period_end_date
        """,
        (
            company_key,
            reporting_period_scope,
        ),
    )


def get_macro_environment() -> pd.DataFrame:
    """Return monthly macroeconomic context."""

    return query_dataframe(
        """
        SELECT
            observation_date,
            federal_funds_rate,
            unemployment_rate,
            consumer_price_index,
            inflation_yoy_rate,
            industrial_production_index,
            industrial_production_yoy_rate
        FROM CREDITPULSE.ANALYTICS.MART_MACRO_ENVIRONMENT
        ORDER BY observation_date
        """
    )


def get_treasury_history() -> pd.DataFrame:
    """Return Treasury yields and curve spreads."""

    return query_dataframe(
        """
        SELECT
            observation_date,
            yield_3m_pct,
            yield_2y_pct,
            yield_5y_pct,
            yield_10y_pct,
            yield_30y_pct,
            spread_10y_2y_pct_points,
            spread_10y_2y_bps,
            spread_10y_3m_pct_points,
            spread_10y_3m_bps,
            is_10y_2y_inverted,
            is_10y_3m_inverted
        FROM CREDITPULSE.ANALYTICS.MART_TREASURY_YIELD_CURVE
        ORDER BY observation_date
        """
    )


def get_pipeline_runs(
    limit: int = 20,
) -> pd.DataFrame:
    """Return recent pipeline execution history."""

    safe_limit = max(
        1,
        min(
            int(limit),
            100,
        ),
    )

    return query_dataframe(
        f"""
        SELECT
            run_id,
            pipeline_name,
            status,
            started_at,
            finished_at,
            duration_seconds,
            execution_environment,
            trigger_type,
            git_sha,
            github_run_id,
            error_message
        FROM CREDITPULSE.CONTROL.PIPELINE_RUNS
        ORDER BY started_at DESC
        LIMIT {safe_limit}
        """
    )