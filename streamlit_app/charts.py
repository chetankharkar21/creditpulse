import pandas as pd
import plotly.graph_objects as go


GRID_COLOR = "rgba(148, 163, 184, 0.14)"
TEXT_COLOR = "#CBD5E1"
MUTED_COLOR = "#94A3B8"


def apply_chart_layout(
    figure: go.Figure,
    *,
    y_title: str | None = None,
) -> go.Figure:
    """Apply consistent CreditPulse chart styling."""

    figure.update_layout(
        template="plotly_dark",
        height=360,
        margin=dict(
            l=10,
            r=20,
            t=20,
            b=20,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(
                size=12,
                color=TEXT_COLOR,
            ),
        ),
        xaxis=dict(
            title=None,
            showgrid=False,
            color=MUTED_COLOR,
        ),
        yaxis=dict(
            title=y_title,
            gridcolor=GRID_COLOR,
            zeroline=False,
            color=MUTED_COLOR,
        ),
    )

    return figure


def liquidity_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create historical current-ratio and cash-ratio chart."""

    data = (
        dataframe[
            [
                "period_end_date",
                "current_ratio",
                "cash_ratio",
            ]
        ]
        .dropna(subset=["period_end_date"])
        .sort_values("period_end_date")
        .copy()
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=data["period_end_date"],
            y=data["current_ratio"],
            mode="lines",
            name="Current Ratio",
            line=dict(
                width=2.5,
            ),
            hovertemplate=(
                "<b>%{x|%b %d, %Y}</b><br>"
                "Current Ratio: %{y:.2f}x"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=data["period_end_date"],
            y=data["cash_ratio"],
            mode="lines",
            name="Cash Ratio",
            line=dict(
                width=2.5,
            ),
            hovertemplate=(
                "<b>%{x|%b %d, %Y}</b><br>"
                "Cash Ratio: %{y:.2f}x"
                "<extra></extra>"
            ),
        )
    )

    apply_chart_layout(
        figure,
        y_title="Ratio",
    )

    figure.update_yaxes(
        tickformat=".1f",
        rangemode="tozero",
    )

    return figure


def cash_position_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create cash and working-capital balance-sheet chart."""

    data = (
        dataframe[
            [
                "period_end_date",
                "cash",
                "current_assets",
                "current_liabilities",
            ]
        ]
        .dropna(subset=["period_end_date"])
        .sort_values("period_end_date")
        .copy()
    )

    # Convert large USD values to billions for presentation.
    for column in [
        "cash",
        "current_assets",
        "current_liabilities",
    ]:
        data[f"{column}_billions"] = (
            data[column] / 1_000_000_000
        )

    figure = go.Figure()

    series = (
        (
            "cash_billions",
            "Cash",
        ),
        (
            "current_assets_billions",
            "Current Assets",
        ),
        (
            "current_liabilities_billions",
            "Current Liabilities",
        ),
    )

    for column, label in series:
        figure.add_trace(
            go.Scatter(
                x=data["period_end_date"],
                y=data[column],
                mode="lines",
                name=label,
                line=dict(
                    width=2.3,
                ),
                hovertemplate=(
                    "<b>%{x|%b %d, %Y}</b><br>"
                    + label
                    + ": $%{y:,.1f}B"
                    + "<extra></extra>"
                ),
            )
        )

    apply_chart_layout(
        figure,
        y_title="USD Billions",
    )

    figure.update_yaxes(
        tickprefix="$",
        ticksuffix="B",
        tickformat=",.0f",
        rangemode="tozero",
    )

    return figure


def performance_value_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create annual revenue and operating cash flow chart."""

    data = (
        dataframe[
            [
                "period_end_date",
                "revenue",
                "operating_cash_flow",
            ]
        ]
        .dropna(subset=["period_end_date"])
        .sort_values("period_end_date")
        .copy()
    )

    data["revenue_billions"] = (
        data["revenue"] / 1_000_000_000
    )

    data["ocf_billions"] = (
        data["operating_cash_flow"] / 1_000_000_000
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=data["period_end_date"],
            y=data["revenue_billions"],
            mode="lines+markers",
            name="Revenue",
            line=dict(
                width=2.5,
            ),
            marker=dict(
                size=6,
            ),
            hovertemplate=(
                "<b>%{x|%Y}</b><br>"
                "Revenue: $%{y:,.1f}B"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=data["period_end_date"],
            y=data["ocf_billions"],
            mode="lines+markers",
            name="Operating Cash Flow",
            line=dict(
                width=2.5,
            ),
            marker=dict(
                size=6,
            ),
            hovertemplate=(
                "<b>%{x|%Y}</b><br>"
                "Operating Cash Flow: $%{y:,.1f}B"
                "<extra></extra>"
            ),
        )
    )

    apply_chart_layout(
        figure,
        y_title="USD Billions",
    )

    figure.update_yaxes(
        tickprefix="$",
        ticksuffix="B",
        tickformat=",.0f",
    )

    return figure


def performance_growth_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create annual margin and year-over-year growth chart."""

    data = (
        dataframe[
            [
                "period_end_date",
                "operating_cash_flow_margin",
                "revenue_yoy_growth",
                "operating_cash_flow_yoy_growth",
            ]
        ]
        .dropna(subset=["period_end_date"])
        .sort_values("period_end_date")
        .copy()
    )

    data["ocf_margin_pct"] = (
        data["operating_cash_flow_margin"] * 100
    )

    data["revenue_growth_pct"] = (
        data["revenue_yoy_growth"] * 100
    )

    data["ocf_growth_pct"] = (
        data["operating_cash_flow_yoy_growth"] * 100
    )

    figure = go.Figure()

    series = (
        (
            "ocf_margin_pct",
            "OCF Margin",
        ),
        (
            "revenue_growth_pct",
            "Revenue Growth",
        ),
        (
            "ocf_growth_pct",
            "OCF Growth",
        ),
    )

    for column, label in series:
        figure.add_trace(
            go.Scatter(
                x=data["period_end_date"],
                y=data[column],
                mode="lines+markers",
                name=label,
                line=dict(
                    width=2.3,
                ),
                marker=dict(
                    size=5,
                ),
                hovertemplate=(
                    "<b>%{x|%Y}</b><br>"
                    + label
                    + ": %{y:.1f}%"
                    + "<extra></extra>"
                ),
            )
        )

    figure.add_hline(
        y=0,
        line_width=1,
        line_dash="dot",
        opacity=0.5,
    )

    apply_chart_layout(
        figure,
        y_title="Percent",
    )

    figure.update_yaxes(
        ticksuffix="%",
        tickformat=".0f",
    )

    return figure


def macro_environment_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create recent macroeconomic environment trend chart."""

    data = (
        dataframe[
            [
                "observation_date",
                "federal_funds_rate",
                "unemployment_rate",
                "inflation_yoy_rate",
                "industrial_production_yoy_rate",
            ]
        ]
        .dropna(subset=["observation_date"])
        .sort_values("observation_date")
        .copy()
    )

    data["observation_date"] = pd.to_datetime(
        data["observation_date"]
    )

    # CreditPulse focuses on the current credit environment.
    # Restrict only the presentation layer to the latest 10 years.
    # The complete historical FRED dataset remains in Snowflake.
    if not data.empty:
        latest_date = data[
            "observation_date"
        ].max()

        start_date = (
            latest_date
            - pd.DateOffset(years=10)
        )

        data = data[
            data["observation_date"] >= start_date
        ].copy()

    # FEDFUNDS and UNRATE are already expressed as
    # percentage-point values in FRED.
    #
    # Inflation and industrial-production YoY metrics
    # are decimal rates from the Gold mart and therefore
    # need conversion to percentage points.
    data["inflation_yoy_pct"] = (
        data["inflation_yoy_rate"] * 100
    )

    data["industrial_production_yoy_pct"] = (
        data["industrial_production_yoy_rate"] * 100
    )

    figure = go.Figure()

    series = (
        (
            "federal_funds_rate",
            "Federal Funds Rate",
        ),
        (
            "unemployment_rate",
            "Unemployment Rate",
        ),
        (
            "inflation_yoy_pct",
            "Inflation YoY",
        ),
        (
            "industrial_production_yoy_pct",
            "Industrial Production YoY",
        ),
    )

    for column, label in series:
        figure.add_trace(
            go.Scatter(
                x=data["observation_date"],
                y=data[column],
                mode="lines",
                name=label,
                line=dict(
                    width=2.2,
                ),
                hovertemplate=(
                    "<b>%{x|%b %Y}</b><br>"
                    + label
                    + ": %{y:.2f}%"
                    + "<extra></extra>"
                ),
            )
        )

    figure.add_hline(
        y=0,
        line_width=1,
        line_dash="dot",
        opacity=0.5,
    )

    apply_chart_layout(
        figure,
        y_title="Percent",
    )

    figure.update_yaxes(
        ticksuffix="%",
        tickformat=".1f",
    )

    return figure


def treasury_yield_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create U.S. Treasury yield-curve history chart."""

    data = (
        dataframe[
            [
                "observation_date",
                "yield_3m_pct",
                "yield_2y_pct",
                "yield_5y_pct",
                "yield_10y_pct",
                "yield_30y_pct",
            ]
        ]
        .dropna(subset=["observation_date"])
        .sort_values("observation_date")
        .copy()
    )

    figure = go.Figure()

    series = (
        (
            "yield_3m_pct",
            "3M",
        ),
        (
            "yield_2y_pct",
            "2Y",
        ),
        (
            "yield_5y_pct",
            "5Y",
        ),
        (
            "yield_10y_pct",
            "10Y",
        ),
        (
            "yield_30y_pct",
            "30Y",
        ),
    )

    for column, label in series:
        figure.add_trace(
            go.Scatter(
                x=data["observation_date"],
                y=data[column],
                mode="lines",
                name=label,
                line=dict(
                    width=2.1,
                ),
                hovertemplate=(
                    "<b>%{x|%b %d, %Y}</b><br>"
                    + label
                    + " Treasury: %{y:.2f}%"
                    + "<extra></extra>"
                ),
            )
        )

    apply_chart_layout(
        figure,
        y_title="Yield",
    )

    figure.update_yaxes(
        ticksuffix="%",
        tickformat=".1f",
        rangemode="tozero",
    )

    return figure


def treasury_spread_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    """Create Treasury term-spread history chart."""

    data = (
        dataframe[
            [
                "observation_date",
                "spread_10y_2y_bps",
                "spread_10y_3m_bps",
            ]
        ]
        .dropna(subset=["observation_date"])
        .sort_values("observation_date")
        .copy()
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=data["observation_date"],
            y=data["spread_10y_2y_bps"],
            mode="lines",
            name="10Y − 2Y",
            line=dict(
                width=2.3,
            ),
            hovertemplate=(
                "<b>%{x|%b %d, %Y}</b><br>"
                "10Y − 2Y: %{y:.0f} bps"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=data["observation_date"],
            y=data["spread_10y_3m_bps"],
            mode="lines",
            name="10Y − 3M",
            line=dict(
                width=2.3,
            ),
            hovertemplate=(
                "<b>%{x|%b %d, %Y}</b><br>"
                "10Y − 3M: %{y:.0f} bps"
                "<extra></extra>"
            ),
        )
    )

    # Zero is economically meaningful:
    # negative values indicate yield-curve inversion.
    figure.add_hline(
        y=0,
        line_width=1,
        line_dash="dot",
        opacity=0.7,
    )

    apply_chart_layout(
        figure,
        y_title="Basis Points",
    )

    figure.update_yaxes(
        ticksuffix=" bps",
        tickformat=",.0f",
    )

    return figure