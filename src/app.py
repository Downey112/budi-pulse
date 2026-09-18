import os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(page_title="BudiPulse", page_icon="🇲🇾", layout="wide")

load_dotenv()

# 2. Database Connection
@st.cache_resource
def init_connection() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        st.error("Missing Supabase credentials. Check your .env file.")
        st.stop()
    return create_client(url, key)

supabase = init_connection()

# 3. Data Ingestion
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    response = supabase.table("fuel_subsidy_records").select("*").execute()
    df = pd.DataFrame(response.data)
    df["date"] = pd.to_datetime(df["date"])
    # Sort chronologically for charting
    return df.sort_values(by="date", ascending=True).reset_index(drop=True)

# 4. App Layout & Sidebar
st.sidebar.image("https://flagcdn.com/w160/my.png", width=100)
st.sidebar.title("BudiPulse Filters")
st.sidebar.markdown("Filter the subsidy gap data by timeframe.")

with st.spinner("Fetching live data from Supabase..."):
    df = load_data()

if df.empty:
    st.warning("No data found in the database.")
    st.stop()

# Date Filter Widget
timeframe = st.sidebar.radio(
    "Select Timeframe:",
    ["All Time", "Last 6 Months", "Last 3 Months"]
)

# Apply Filter
if timeframe == "Last 6 Months":
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=6)
    df = df[df["date"] >= cutoff]
elif timeframe == "Last 3 Months":
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=3)
    df = df[df["date"] >= cutoff]

# Main Page Header
st.title("BudiPulse 🇲🇾")
st.markdown("### Tracking Malaysia's Fuel Subsidy Rationalization & Fiscal Gaps")
st.markdown("Automated data pipeline tracking the spread between market float prices and BUDI MADANI retail caps.")
st.write("") # Spacer

# 5. KPI Metrics Row (Styled)
latest = df.iloc[-1]
latest_date = latest['date'].strftime('%d %B %Y')

st.markdown(f"**Latest Data Update:** `{latest_date}`")

# Use containers to give metrics breathing room
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("RON95 Market", f"RM {latest['ron95_market']:.2f}")
with col2:
    st.metric("RON95 Subsidy Gap", f"RM {latest['ron95_gap']:.2f}", delta=f"RM {latest['ron95_gap']:.2f}", delta_color="inverse")
with col3:
    st.metric("Diesel Market", f"RM {latest['diesel_market']:.2f}")
with col4:
    st.metric("Diesel Subsidy Gap", f"RM {latest['diesel_gap']:.2f}", delta=f"RM {latest['diesel_gap']:.2f}", delta_color="inverse")

st.divider()

# 6. Premium Interactive Visualization
st.subheader("Subsidy Gap Trends Over Time")

plot_df = df.dropna(subset=['ron95_gap', 'diesel_gap'])

if not plot_df.empty:
    fig = px.line(
        plot_df, 
        x="date", 
        y=["ron95_gap", "diesel_gap"],
        color_discrete_map={
            "ron95_gap": "#F5B041", 
            "diesel_gap": "#3498DB" 
        }
    )
    
    # Advanced Plotly Styling
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="Subsidy Gap (RM / Liter)",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    # Clean up gridlines
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#333333")
    
    # Clean legend names
    fig.for_each_trace(lambda t: t.update(name={'ron95_gap': 'RON95 Gap', 'diesel_gap': 'Diesel Gap'}[t.name]))
    
    # Draw chart with custom config to remove the ugly default Plotly toolbar
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Not enough data to plot subsidy gaps yet.")

# 7. Raw Data Table
st.write("")
with st.expander("🔍 View Raw Database Records"):
    st.dataframe(
        df.sort_values(by="date", ascending=False), 
        use_container_width=True, 
        hide_index=True
    )