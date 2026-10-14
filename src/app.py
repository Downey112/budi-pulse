import os
from typing import Dict, Tuple
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

st.set_page_config(
    page_title="BudiPulse",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

PRICE_COLS = ["ron95_market", "ron95_gap", "diesel_market", "diesel_gap"]
ALL_NUMERIC_COLS = [
    "ron95_market",
    "ron95_budi",
    "ron95_gap",
    "diesel_market",
    "diesel_budi",
    "diesel_gap",
]


@st.cache_resource
def init_connection() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        st.error("Missing Supabase credentials. Check your .env file.")
        st.stop()
    return create_client(url, key)


supabase = init_connection()

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-base: #090A0F;
        --bg-surface: #11131A;
        --bg-elevated: #161922;
        --border-subtle: #1E212D;
        --border-hover: #2E3346;
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --accent-ron95: #E5A000;
        --accent-diesel: #38BDF8;
        --delta-up: #EF4444;
        --delta-down: #10B981;
        --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
        -webkit-font-smoothing: antialiased;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1180px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0C0E14 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    @keyframes bp-fade-up {
        from {
            opacity: 0;
            transform: translateY(6px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes bp-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.35; }
    }

    .bp-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        flex-wrap: wrap;
        gap: 12px;
        padding-bottom: 20px;
        margin-bottom: 24px;
        border-bottom: 1px solid var(--border-subtle);
        animation: bp-fade-up 200ms var(--ease-out) both;
    }

    .bp-title {
        font-size: 24px;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-primary);
        margin: 0 0 4px 0;
        line-height: 1.2;
    }

    .bp-subtitle {
        font-size: 13.5px;
        color: var(--text-secondary);
        margin: 0;
        font-weight: 400;
    }

    .bp-meta-pill {
        font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;
        font-size: 12px;
        color: var(--text-secondary);
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 6px 10px;
        font-variant-numeric: tabular-nums;
    }

    .bp-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 20px 22px;
        transition: border-color 160ms var(--ease-out), background-color 160ms var(--ease-out);
        animation: bp-fade-up 240ms var(--ease-out) both;
    }

    .bp-card:hover {
        border-color: var(--border-hover);
        background: var(--bg-elevated);
    }

    .bp-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .bp-label {
        font-size: 11.5px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .bp-swatch {
        width: 8px;
        height: 8px;
        border-radius: 2px;
        display: inline-block;
    }

    .bp-delta {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 12px;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
        padding: 2px 7px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.03);
    }

    .bp-value {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 30px;
        font-weight: 600;
        letter-spacing: -0.03em;
        color: var(--text-primary);
        line-height: 1.15;
        font-variant-numeric: tabular-nums;
    }

    .bp-unit {
        font-size: 14px;
        font-weight: 400;
        color: var(--text-muted);
    }

    .bp-card-foot {
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid var(--border-subtle);
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-variant-numeric: tabular-nums;
    }

    .bp-section {
        margin-top: 32px;
        margin-bottom: 12px;
        animation: bp-fade-up 260ms var(--ease-out) both;
    }

    .bp-section-title {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: var(--text-primary);
        margin: 0 0 2px 0;
    }

    .bp-section-desc {
        font-size: 13px;
        color: var(--text-muted);
        margin: 0;
    }

    .bp-calc-panel {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 22px;
        height: 100%;
        transition: border-color 160ms var(--ease-out);
    }

    .bp-calc-panel:hover {
        border-color: var(--border-hover);
    }

    .bp-progress-header {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-bottom: 8px;
        color: var(--text-secondary);
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-variant-numeric: tabular-nums;
    }

    .bp-progress-track {
        width: 100%;
        height: 6px;
        background: #1C1F2B;
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 20px;
    }

    .bp-progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 240ms var(--ease-out), background-color 200ms ease;
    }

    .bp-calc-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 14px;
    }

    .bp-stat-box {
        background: #0D0F15;
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 14px 16px;
    }

    .bp-stat-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 6px;
    }

    .bp-stat-val {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 20px;
        font-weight: 600;
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
    }

    .bp-stat-sub {
        font-size: 11.5px;
        color: var(--text-secondary);
        margin-top: 4px;
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-variant-numeric: tabular-nums;
    }

    .bp-status-row {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 6px;
    }

    .bp-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--delta-down);
        animation: bp-pulse 3s ease-in-out infinite;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_data() -> pd.DataFrame:
    response = supabase.table("fuel_subsidy_records").select("*").execute()
    df = pd.DataFrame(response.data)
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    for col in ALL_NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = float("nan")

    return df.sort_values(by="date", ascending=True, ignore_index=True)


def delta_style(delta: float) -> Tuple[str, str]:
    if delta > 0:
        return "color: #EF4444;", "+"
    if delta < 0:
        return "color: #10B981;", "-"
    return "color: #6B7280;", ""


def compute_commute_impact(
    dist_km: float,
    eff_kml: float,
    days: int,
    market_price: float,
    subsidy_gap: float,
    is_4wd: bool,
) -> Dict[str, float]:
    monthly_km = dist_km * days
    monthly_liters = monthly_km / max(eff_kml, 0.1)
    subsidized_price = max(0.0, market_price - subsidy_gap)
    quota = 400.0 if is_4wd else 300.0

    liters_subsidized = min(monthly_liters, quota)
    liters_market = max(0.0, monthly_liters - quota)

    cost_subsidized = liters_subsidized * subsidized_price
    cost_market = liters_market * market_price
    total_monthly_cost = cost_subsidized + cost_market
    cost_no_subsidy = monthly_liters * market_price
    gov_absorbed = max(0.0, cost_no_subsidy - total_monthly_cost)
    utilization_pct = (monthly_liters / quota) * 100.0

    return {
        "monthly_km": monthly_km,
        "monthly_liters": monthly_liters,
        "subsidized_price": subsidized_price,
        "market_price": market_price,
        "quota": quota,
        "liters_subsidized": liters_subsidized,
        "liters_market": liters_market,
        "cost_market": cost_market,
        "total_monthly_cost": total_monthly_cost,
        "gov_absorbed": gov_absorbed,
        "utilization_pct": utilization_pct,
    }


try:
    df = load_data()
except Exception as err:
    st.error(
        f"Could not load data from Supabase. Verify SUPABASE_URL and project status.\n\n`{type(err).__name__}: {err}`"
    )
    st.stop()

if df.empty:
    st.warning("No data found in the production schema.")
    st.stop()

st.sidebar.markdown(
    """
    <div style="padding: 8px 0 16px 0; border-bottom: 1px solid #1E212D; margin-bottom: 16px;">
        <div style="font-size: 16px; font-weight: 600; color: #F3F4F6; letter-spacing: -0.02em;">BudiPulse</div>
        <div style="font-size: 12px; color: #6B7280; margin-top: 2px;">Malaysia Fuel Subsidy Telemetry</div>
    </div>
    """,
    unsafe_allow_html=True,
)

timeframe = st.sidebar.radio(
    "Timeframe",
    ["All Time", "Last 6 Months", "Last 3 Months"],
    index=1,
)

max_date = df["date"].max()
if timeframe == "Last 6 Months":
    cutoff = max_date - pd.DateOffset(months=6)
    filtered_df = df.loc[df["date"] >= cutoff]
elif timeframe == "Last 3 Months":
    cutoff = max_date - pd.DateOffset(months=3)
    filtered_df = df.loc[df["date"] >= cutoff]
else:
    filtered_df = df

st.sidebar.markdown(
    """
    <div style="margin-top: 28px; padding-top: 16px; border-top: 1px solid #1E212D;">
        <div class="bp-status-row">
            <span class="bp-dot"></span>
            <span>Pipeline active</span>
        </div>
        <div style="font-size: 11.5px; color: #6B7280; font-family: 'JetBrains Mono', monospace;">
            Sync: Sun &amp; Wed 00:00 UTC
        </div>
        <div style="font-size: 11.5px; color: #6B7280; margin-top: 4px;">
            Source: OpenDOSM fuelprice.csv
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

priced_df = df.dropna(subset=PRICE_COLS)
if priced_df.empty:
    st.warning("No complete pricing records (market price + subsidy gap) are available yet.")
    st.stop()

latest = priced_df.iloc[-1]
prev = priced_df.iloc[-2] if len(priced_df) >= 2 else latest
latest_date = latest["date"].strftime("%d %b %Y")

st.markdown(
    f"""
    <div class="bp-header">
        <div>
            <h1 class="bp-title">BudiPulse</h1>
            <p class="bp-subtitle">Weekly spread between unsubsidized float prices and BUDI MADANI retail caps</p>
        </div>
        <div class="bp-meta-pill">Updated {latest_date}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

ron95_delta_gap = round(float(latest["ron95_gap"] - prev["ron95_gap"]), 2)
diesel_delta_gap = round(float(latest["diesel_gap"] - prev["diesel_gap"]), 2)

ron95_style, ron95_sign = delta_style(ron95_delta_gap)
diesel_style, diesel_sign = delta_style(diesel_delta_gap)

ron95_budi_val = float(latest["ron95_market"] - latest["ron95_gap"])
diesel_budi_val = float(latest["diesel_market"] - latest["diesel_gap"])

col_ron95, col_diesel = st.columns(2, gap="medium")

with col_ron95:
    st.markdown(
        f"""
        <div class="bp-card">
            <div class="bp-card-top">
                <span class="bp-label"><span class="bp-swatch" style="background:#E5A000;"></span>RON95 Subsidy Spread</span>
                <span class="bp-delta" style="{ron95_style}">{ron95_sign}RM {abs(ron95_delta_gap):.2f} WoW</span>
            </div>
            <div class="bp-value">RM {latest['ron95_gap']:.2f} <span class="bp-unit">/ L</span></div>
            <div class="bp-card-foot">
                <span>Float: RM {latest['ron95_market']:.2f}/L</span>
                <span>Cap: RM {ron95_budi_val:.2f}/L</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_diesel:
    st.markdown(
        f"""
        <div class="bp-card">
            <div class="bp-card-top">
                <span class="bp-label"><span class="bp-swatch" style="background:#38BDF8;"></span>Diesel Subsidy Spread</span>
                <span class="bp-delta" style="{diesel_style}">{diesel_sign}RM {abs(diesel_delta_gap):.2f} WoW</span>
            </div>
            <div class="bp-value">RM {latest['diesel_gap']:.2f} <span class="bp-unit">/ L</span></div>
            <div class="bp-card-foot">
                <span>Float: RM {latest['diesel_market']:.2f}/L</span>
                <span>Cap: RM {diesel_budi_val:.2f}/L</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="bp-section">
        <h2 class="bp-section-title">Historical Spread</h2>
        <p class="bp-section-desc">Per-liter fiscal gap absorbed between market float and subsidized retail price</p>
    </div>
    """,
    unsafe_allow_html=True,
)

plot_df = filtered_df.dropna(subset=["ron95_gap", "diesel_gap"], how="all")

if not plot_df.empty:
    fig = px.line(
        plot_df,
        x="date",
        y=["ron95_gap", "diesel_gap"],
        color_discrete_map={
            "ron95_gap": "#E5A000",
            "diesel_gap": "#38BDF8",
        },
    )
    fig.update_traces(
        line=dict(width=2),
        hovertemplate="RM %{y:.2f}/L<extra></extra>",
    )
    fig.update_layout(
        height=370,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="RM / Liter",
        legend_title_text="",
        font=dict(family="Inter, sans-serif", size=12, color="#9CA3AF"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#9CA3AF"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#11131A",
            bordercolor="#2E3346",
            font=dict(family="JetBrains Mono, monospace", size=12, color="#F3F4F6"),
        ),
        margin=dict(l=0, r=32, t=48, b=8),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#1E212D",
        tickformat="%b %Y",
        tickfont=dict(color="#6B7280", size=11),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#161922",
        zeroline=False,
        linecolor="rgba(0,0,0,0)",
        tickprefix="RM ",
        tickfont=dict(color="#6B7280", size=11),
    )
    trace_labels = {"ron95_gap": "RON95 Spread", "diesel_gap": "Diesel Spread"}
    fig.for_each_trace(lambda t: t.update(name=trace_labels.get(t.name, t.name)))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
else:
    st.info("Insufficient longitudinal data to plot subsidy gap trends for this timeframe.")

st.markdown(
    """
    <div class="bp-section">
        <h2 class="bp-section-title">Commute Quota Calculator</h2>
        <p class="bp-section-desc">Estimate monthly fuel expenditure against the 300 L standard quota (400 L for qualifying 4WD / pickups)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

_fragment_decorator = getattr(st, "fragment", lambda fn: fn)


@_fragment_decorator
def render_calculator(latest_row: pd.Series) -> None:
    calc_col1, calc_col2 = st.columns([1, 1.35], gap="large")

    with calc_col1:
        calc_fuel = st.selectbox("Vehicle Fuel Type", ["RON95", "Diesel"])
        is_4wd = st.checkbox("Pickup / 4WD (400 L Quota Eligibility)")
        calc_dist = st.number_input(
            "Daily Round-Trip Distance (km)",
            min_value=1.0,
            value=40.0,
            step=5.0,
        )
        calc_eff = st.number_input(
            "Vehicle Efficiency (km/L)",
            min_value=1.0,
            value=14.0,
            help="Compact sedans average ~14 km/L; larger SUVs/pickups average ~10 km/L.",
        )
        calc_days = st.slider("Driving Days per Month", 1, 31, 22)

    with calc_col2:
        if calc_fuel == "RON95":
            market_price = float(latest_row["ron95_market"])
            subsidy_gap = float(latest_row["ron95_gap"])
        else:
            market_price = float(latest_row["diesel_market"])
            subsidy_gap = float(latest_row["diesel_gap"])

        stats = compute_commute_impact(
            dist_km=calc_dist,
            eff_kml=calc_eff,
            days=calc_days,
            market_price=market_price,
            subsidy_gap=subsidy_gap,
            is_4wd=is_4wd,
        )

        bar_pct = min(100.0, stats["utilization_pct"])
        if stats["liters_market"] > 0:
            bar_color = "#EF4444"
            quota_status = f"{stats['liters_market']:.1f} L over {int(stats['quota'])} L cap"
        elif stats["utilization_pct"] >= 85.0:
            bar_color = "#E5A000"
            quota_status = f"Within {int(stats['quota'])} L cap ({stats['utilization_pct']:.0f}%)"
        else:
            bar_color = "#10B981"
            quota_status = f"Within {int(stats['quota'])} L cap ({stats['utilization_pct']:.0f}%)"

        st.markdown(
            f"""
            <div class="bp-calc-panel">
                <div class="bp-progress-header">
                    <span>Quota Usage: {stats['monthly_liters']:.1f} L / {int(stats['quota'])} L</span>
                    <span>{quota_status}</span>
                </div>
                <div class="bp-progress-track">
                    <div class="bp-progress-fill" style="width: {bar_pct:.1f}%; background-color: {bar_color};"></div>
                </div>
                <div class="bp-calc-grid">
                    <div class="bp-stat-box">
                        <div class="bp-stat-label">Total Fuel Required</div>
                        <div class="bp-stat-val">{stats['monthly_liters']:.1f} L</div>
                        <div class="bp-stat-sub">{stats['monthly_km']:.0f} km / month</div>
                    </div>
                    <div class="bp-stat-box">
                        <div class="bp-stat-label">Effective Monthly Cost</div>
                        <div class="bp-stat-val">RM {stats['total_monthly_cost']:.2f}</div>
                        <div class="bp-stat-sub">Cap rate RM {stats['subsidized_price']:.2f}/L</div>
                    </div>
                    <div class="bp-stat-box">
                        <div class="bp-stat-label">Unsubsidized Exposure</div>
                        <div class="bp-stat-val">RM {stats['cost_market']:.2f}</div>
                        <div class="bp-stat-sub">{stats['liters_market']:.1f} L @ RM {stats['market_price']:.2f}/L</div>
                    </div>
                    <div class="bp-stat-box">
                        <div class="bp-stat-label">Subsidy Absorbed</div>
                        <div class="bp-stat-val" style="color: #10B981;">RM {stats['gov_absorbed']:.2f}</div>
                        <div class="bp-stat-sub">{stats['liters_subsidized']:.1f} L subsidized</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_calculator(latest)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

governance_df = filtered_df.sort_values(by="date", ascending=False, ignore_index=True)
display_cols = [
    c
    for c in [
        "date",
        "ron95_market",
        "ron95_budi",
        "ron95_gap",
        "diesel_market",
        "diesel_budi",
        "diesel_gap",
    ]
    if c in governance_df.columns
]

with st.expander(f"Historical price records ({len(governance_df)} weeks)", expanded=False):
    col_cfg = {}
    if hasattr(st, "column_config"):
        col_cfg = {
            "date": st.column_config.DateColumn("Week", format="YYYY-MM-DD"),
            "ron95_market": st.column_config.NumberColumn("RON95 Float", format="RM %.2f"),
            "ron95_budi": st.column_config.NumberColumn("RON95 Cap", format="RM %.2f"),
            "ron95_gap": st.column_config.NumberColumn("RON95 Spread", format="RM %.2f"),
            "diesel_market": st.column_config.NumberColumn("Diesel Float", format="RM %.2f"),
            "diesel_budi": st.column_config.NumberColumn("Diesel Cap", format="RM %.2f"),
            "diesel_gap": st.column_config.NumberColumn("Diesel Spread", format="RM %.2f"),
        }
    st.dataframe(
        governance_df[display_cols],
        width="stretch",
        hide_index=True,
        column_config=col_cfg,
    )