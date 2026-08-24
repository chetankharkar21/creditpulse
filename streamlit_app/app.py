import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# -------------------------------------------------------------------
# Project path configuration
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from streamlit_app.charts import (  # noqa: E402
    cash_position_chart,
    liquidity_chart,
    macro_environment_chart,
    performance_growth_chart,
    performance_value_chart,
    treasury_spread_chart,
    treasury_yield_chart,
)
from streamlit_app.data_access import (  # noqa: E402
    get_companies,
    get_liquidity_history,
    get_macro_environment,
    get_performance_history,
    get_pipeline_runs,
    get_treasury_history,
)


# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="CreditPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------------------------------------------------
# Application styling
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        [data-testid="stMetric"] {
            border: 1px solid rgba(120, 120, 120, 0.20);
            border-radius: 10px;
            padding: 16px 18px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(120, 120, 120, 0.15);
        }

        .creditpulse-subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-top: -0.5rem;
            margin-bottom: 1.5rem;
        }

        .section-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6b7280;
            margin-top: 1rem;
            margin-bottom: 0.35rem;
        }

        .source-note {
            color: #6b7280;
            font-size: 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Cached data loaders
# -------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_companies():
    """Load the governed CreditPulse company universe."""

    return get_companies()


@st.cache_data(ttl=600)
def load_liquidity(company_key: str):
    """Load liquidity history for a selected company."""

    return get_liquidity_history(company_key)


@st.cache_data(ttl=600)
def load_performance(company_key: str):
    """Load annual performance history for a selected company."""

    return get_performance_history(company_key)


@st.cache_data(ttl=600)
def load_macro_environment():
    """Load FRED macroeconomic context."""

    return get_macro_environment()


@st.cache_data(ttl=600)
def load_treasury_history():
    """Load Treasury yield-curve history."""

    return get_treasury_history()


@st.cache_data(ttl=300)
def load_pipeline_runs():
    """Load recent CreditPulse pipeline execution history."""

    return get_pipeline_runs(limit=10)


# -------------------------------------------------------------------
# Formatting helpers
# -------------------------------------------------------------------
def is_missing(value) -> bool:
    """Return True when a value is null or NaN."""

    return value is None or pd.isna(value)


def format_ratio(value) -> str:
    """Format a financial ratio."""

    if is_missing(value):
        return "—"

    return f"{float(value):.2f}x"


def format_percent(value) -> str:
    """Format a decimal value as a percentage."""

    if is_missing(value):
        return "—"

    return f"{float(value) * 100:.1f}%"


def format_percentage_points(value) -> str:
    """Format values already expressed as percentage points."""

    if is_missing(value):
        return "—"

    return f"{float(value):.2f}%"


def format_bps(value) -> str:
    """Format basis-point values."""

    if is_missing(value):
        return "—"

    return f"{float(value):.0f} bps"


def format_environment(value) -> str:
    """Convert execution environment to a clean display label."""

    labels = {
        "GITHUB_ACTIONS": "GitHub Actions",
        "LOCAL": "Local",
    }

    normalized_value = str(value).upper()

    return labels.get(
        normalized_value,
        str(value).replace("_", " ").title(),
    )


def format_trigger(value) -> str:
    """Convert pipeline trigger type to a clean display label."""

    labels = {
        "workflow_dispatch": "Manual Trigger",
        "schedule": "Scheduled",
        "manual_local": "Local Manual",
    }

    normalized_value = str(value)

    return labels.get(
        normalized_value,
        normalized_value.replace("_", " ").title(),
    )


def clean_company_name(name: str) -> str:
    """Improve SEC company-name formatting."""

    if name.isupper():
        return name.title()

    return name


def latest_non_null(
    dataframe: pd.DataFrame,
    column: str,
):
    """
    Return the latest non-null value and its observation date.

    Different macroeconomic series can have slightly different
    publication availability, so each KPI is resolved independently.
    """

    valid = (
        dataframe[
            [
                "observation_date",
                column,
            ]
        ]
        .dropna(
            subset=[
                "observation_date",
                column,
            ]
        )
        .sort_values("observation_date")
    )

    if valid.empty:
        return None, None

    latest = valid.iloc[-1]

    return (
        latest[column],
        latest["observation_date"],
    )


# -------------------------------------------------------------------
# Load company universe
# -------------------------------------------------------------------
try:
    companies = load_companies()

except Exception as exc:
    st.error(
        "CreditPulse could not connect to the analytics platform."
    )

    st.caption(
        "Verify the Snowflake connection configuration and try again."
    )

    st.exception(exc)
    st.stop()


if companies.empty:
    st.warning(
        "No companies are currently available in the "
        "CreditPulse company universe."
    )
    st.stop()


company_options = {
    clean_company_name(row.company_name): row.company_key
    for row in companies.itertuples()
}


# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("## CreditPulse")

    st.caption(
        "Corporate Credit & Liquidity Risk Intelligence"
    )

    st.divider()

    selected_company_name = st.selectbox(
        "Company",
        options=list(company_options.keys()),
        index=0,
    )

    selected_company_key = company_options[
        selected_company_name
    ]

    st.divider()

    st.markdown(
        """
        <div class="source-note">
            Sources<br>
            SEC EDGAR · Federal Reserve · U.S. Treasury
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------
# Load selected-company data
# -------------------------------------------------------------------
try:
    liquidity = load_liquidity(
        selected_company_key
    )

    performance = load_performance(
        selected_company_key
    )

except Exception as exc:
    st.error(
        "Financial data could not be loaded for the "
        "selected company."
    )

    st.exception(exc)
    st.stop()


# -------------------------------------------------------------------
# Load macro and market context
# -------------------------------------------------------------------
try:
    macro = load_macro_environment()
    treasury = load_treasury_history()

except Exception:
    macro = pd.DataFrame()
    treasury = pd.DataFrame()


# -------------------------------------------------------------------
# Page header
# -------------------------------------------------------------------
st.title(selected_company_name)

st.markdown(
    """
    <div class="creditpulse-subtitle">
        Financial health, cash-generation and liquidity intelligence
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Validate liquidity availability
# -------------------------------------------------------------------
if liquidity.empty:
    st.warning(
        "No liquidity history is available for this company."
    )
    st.stop()


latest_liquidity = (
    liquidity
    .sort_values("period_end_date")
    .iloc[-1]
)


latest_performance = None

if not performance.empty:
    latest_performance = (
        performance
        .sort_values("period_end_date")
        .iloc[-1]
    )


# -------------------------------------------------------------------
# Latest financial signals
# -------------------------------------------------------------------
st.markdown(
    """
    <div class="section-label">
        Latest Financial Signals
    </div>
    """,
    unsafe_allow_html=True,
)


col1, col2, col3, col4, col5, col6 = st.columns(6)


with col1:
    st.metric(
        "Current Ratio",
        format_ratio(
            latest_liquidity["current_ratio"]
        ),
    )


with col2:
    st.metric(
        "Cash Ratio",
        format_ratio(
            latest_liquidity["cash_ratio"]
        ),
    )


with col3:
    st.metric(
        "Cash / Assets",
        format_percent(
            latest_liquidity[
                "cash_to_assets_ratio"
            ]
        ),
    )


with col4:
    st.metric(
        "OCF Margin",
        (
            format_percent(
                latest_performance[
                    "operating_cash_flow_margin"
                ]
            )
            if latest_performance is not None
            else "—"
        ),
    )


with col5:
    st.metric(
        "Revenue Growth",
        (
            format_percent(
                latest_performance[
                    "revenue_yoy_growth"
                ]
            )
            if latest_performance is not None
            else "—"
        ),
    )


with col6:
    st.metric(
        "OCF Growth",
        (
            format_percent(
                latest_performance[
                    "operating_cash_flow_yoy_growth"
                ]
            )
            if latest_performance is not None
            else "—"
        ),
    )


latest_liquidity_date = pd.to_datetime(
    latest_liquidity["period_end_date"]
).strftime("%B %d, %Y")


st.caption(
    f"Latest liquidity reporting period: "
    f"{latest_liquidity_date}"
)


# -------------------------------------------------------------------
# Liquidity section
# -------------------------------------------------------------------
st.divider()


left, right = st.columns(
    2,
    gap="large",
)


with left:
    st.subheader("Liquidity")

    st.caption(
        "Current ratio and cash ratio across reported periods"
    )

    st.plotly_chart(
        liquidity_chart(
            liquidity
        ),
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


with right:
    st.subheader("Cash Position")

    st.caption(
        "Cash, current assets and current liabilities"
    )

    st.plotly_chart(
        cash_position_chart(
            liquidity
        ),
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# -------------------------------------------------------------------
# Financial performance section
# -------------------------------------------------------------------
st.divider()


st.markdown(
    """
    <div class="section-label">
        Financial Performance
    </div>
    """,
    unsafe_allow_html=True,
)


if performance.empty:
    st.info(
        "Annual revenue and operating cash flow history "
        "is not available for this company."
    )

else:
    latest_performance_date = pd.to_datetime(
        performance["period_end_date"].max()
    ).strftime("%B %d, %Y")

    st.caption(
        "Annual operating performance · "
        f"latest period ending {latest_performance_date}"
    )

    performance_left, performance_right = st.columns(
        2,
        gap="large",
    )


    with performance_left:
        st.subheader(
            "Revenue & Operating Cash Flow"
        )

        st.caption(
            "Annual revenue and cash generated from operations"
        )

        st.plotly_chart(
            performance_value_chart(
                performance
            ),
            width="stretch",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


    with performance_right:
        st.subheader(
            "Margins & Growth"
        )

        st.caption(
            "OCF margin and year-over-year operating performance"
        )

        st.plotly_chart(
            performance_growth_chart(
                performance
            ),
            width="stretch",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


# -------------------------------------------------------------------
# Macro & rates section
# -------------------------------------------------------------------
st.divider()


st.markdown(
    """
    <div class="section-label">
        Macro & Rates Environment
    </div>
    """,
    unsafe_allow_html=True,
)


st.caption(
    "External economic and interest-rate context for "
    "corporate credit analysis"
)


if macro.empty or treasury.empty:
    st.info(
        "Macroeconomic or Treasury context is currently unavailable."
    )

else:
    fed_funds, fed_date = latest_non_null(
        macro,
        "federal_funds_rate",
    )

    unemployment, unemployment_date = latest_non_null(
        macro,
        "unemployment_rate",
    )

    inflation, inflation_date = latest_non_null(
        macro,
        "inflation_yoy_rate",
    )

    industrial_production, industrial_date = latest_non_null(
        macro,
        "industrial_production_yoy_rate",
    )


    latest_treasury = (
        treasury
        .dropna(subset=["observation_date"])
        .sort_values("observation_date")
        .iloc[-1]
    )


    macro1, macro2, macro3, macro4, macro5, macro6 = (
        st.columns(6)
    )


    with macro1:
        st.metric(
            "Fed Funds",
            format_percentage_points(
                fed_funds
            ),
        )


    with macro2:
        st.metric(
            "Inflation YoY",
            format_percent(
                inflation
            ),
        )


    with macro3:
        st.metric(
            "Unemployment",
            format_percentage_points(
                unemployment
            ),
        )


    with macro4:
        st.metric(
            "10Y Treasury",
            format_percentage_points(
                latest_treasury[
                    "yield_10y_pct"
                ]
            ),
        )


    with macro5:
        st.metric(
            "10Y − 2Y Spread",
            format_bps(
                latest_treasury[
                    "spread_10y_2y_bps"
                ]
            ),
        )


    with macro6:
        is_inverted = bool(
            latest_treasury[
                "is_10y_2y_inverted"
            ]
        )

        st.metric(
            "10Y − 2Y Curve",
            (
                "Inverted"
                if is_inverted
                else "Positive"
            ),
        )


    treasury_date = pd.to_datetime(
        latest_treasury["observation_date"]
    ).strftime("%B %d, %Y")


    macro_dates = [
        date
        for date in [
            fed_date,
            unemployment_date,
            inflation_date,
            industrial_date,
        ]
        if date is not None
    ]


    if macro_dates:
        macro_latest_date = pd.to_datetime(
            max(macro_dates)
        ).strftime("%B %Y")

        st.caption(
            f"Latest macro observations through "
            f"{macro_latest_date} · "
            f"Treasury curve through {treasury_date}"
        )


    st.markdown(
        "#### Economic Environment"
    )

    st.caption(
        "Policy rates, labor conditions, inflation and "
        "industrial-production growth"
    )

    st.plotly_chart(
        macro_environment_chart(
            macro
        ),
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


    rates_left, rates_right = st.columns(
        2,
        gap="large",
    )


    with rates_left:
        st.subheader(
            "Treasury Yields"
        )

        st.caption(
            "U.S. Treasury term structure across key maturities"
        )

        st.plotly_chart(
            treasury_yield_chart(
                treasury
            ),
            width="stretch",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


    with rates_right:
        st.subheader(
            "Yield Curve Spreads"
        )

        st.caption(
            "10Y−2Y and 10Y−3M term spreads; "
            "values below zero indicate inversion"
        )

        st.plotly_chart(
            treasury_spread_chart(
                treasury
            ),
            width="stretch",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


# -------------------------------------------------------------------
# Platform health & data freshness
# -------------------------------------------------------------------
st.divider()


st.markdown(
    """
    <div class="section-label">
        Platform Health & Data Freshness
    </div>
    """,
    unsafe_allow_html=True,
)


st.caption(
    "Operational status of the automated CreditPulse data platform"
)


try:
    pipeline_runs = load_pipeline_runs()

except Exception:
    pipeline_runs = pd.DataFrame()


if pipeline_runs.empty:
    st.info(
        "Pipeline execution history is currently unavailable."
    )

else:
    latest_run = (
        pipeline_runs
        .sort_values(
            "started_at",
            ascending=False,
        )
        .iloc[0]
    )

    status = str(
        latest_run["status"]
    ).upper()

    environment = format_environment(
        latest_run[
            "execution_environment"
        ]
    )

    trigger = format_trigger(
        latest_run[
            "trigger_type"
        ]
    )

    duration = latest_run[
        "duration_seconds"
    ]

    started_at = pd.to_datetime(
        latest_run["started_at"],
        utc=True,
    )

    git_sha = latest_run[
        "git_sha"
    ]

    github_run_id = latest_run[
        "github_run_id"
    ]


    run1, run2, run3, run4 = st.columns(4)


    with run1:
        st.metric(
            "Pipeline Status",
            status,
        )


    with run2:
        st.metric(
            "Last Runtime",
            (
                f"{float(duration):.1f}s"
                if not is_missing(duration)
                else "—"
            ),
        )


    with run3:
        st.metric(
            "Environment",
            environment,
        )


    with run4:
        st.metric(
            "Trigger",
            trigger,
        )


    st.caption(
        "Latest platform execution: "
        f"{started_at.strftime('%B %d, %Y %H:%M UTC')}"
    )


    metadata_parts = []


    if not is_missing(git_sha):
        metadata_parts.append(
            f"Git SHA {str(git_sha)[:8]}"
        )


    if not is_missing(github_run_id):
        metadata_parts.append(
            f"GitHub Run {github_run_id}"
        )


    if metadata_parts:
        st.caption(
            " · ".join(
                metadata_parts
            )
        )


    error_message = latest_run[
        "error_message"
    ]


    if (
        status == "FAILED"
        and not is_missing(error_message)
    ):
        st.error(
            f"Latest pipeline failure: {error_message}"
        )


# -------------------------------------------------------------------
# Data freshness summary
# -------------------------------------------------------------------
fresh1, fresh2, fresh3 = st.columns(3)


with fresh1:
    sec_freshness = pd.to_datetime(
        liquidity[
            "period_end_date"
        ].max()
    ).strftime("%b %d, %Y")

    st.metric(
        "SEC Data Through",
        sec_freshness,
    )


with fresh2:
    if not macro.empty:
        macro_freshness = pd.to_datetime(
            macro[
                "observation_date"
            ].max()
        ).strftime("%b %Y")

        st.metric(
            "Macro Data Through",
            macro_freshness,
        )

    else:
        st.metric(
            "Macro Data Through",
            "—",
        )


with fresh3:
    if not treasury.empty:
        treasury_freshness = pd.to_datetime(
            treasury[
                "observation_date"
            ].max()
        ).strftime("%b %d, %Y")

        st.metric(
            "Treasury Data Through",
            treasury_freshness,
        )

    else:
        st.metric(
            "Treasury Data Through",
            "—",
        )


# -------------------------------------------------------------------
# Methodology note
# -------------------------------------------------------------------
st.divider()


st.caption(
    "CreditPulse uses latest-known SEC financial data with "
    "Federal Reserve and U.S. Treasury market context. "
    "Metrics are analytical signals and do not represent "
    "a credit rating or probability of default."
)