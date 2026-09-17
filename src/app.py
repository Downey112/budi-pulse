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

# 4. App Layout
st.title("BudiPulse 🇲🇾")
st.markdown("Tracking Malaysia's Fuel Subsidy Rationalization & Fiscal Gaps")

with st.spinner("Fetching live data from Supabase..."):
    df = load_data()

if df.empty:
    st.warning("No data found in the database.")
    st.stop()

# 5. KPI Metrics Row
latest = df.iloc[-1]
latest_date = latest['date'].strftime('%d %B %Y')

st.write(f"**Latest Update:** {latest_date}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("RON95 Market", f"RM {latest['ron95_market']:.2f}")
with col2:
    st.metric("RON95 Subsidy Gap", f"RM {latest['ron95_gap']:.2f}")
with col3:
    st.metric("Diesel Market", f"RM {latest['diesel_market']:.2f}")
with col4:
    st.metric("Diesel Subsidy Gap", f"RM {latest['diesel_gap']:.2f}")

st.divider()

# 6. Interactive Visualization
st.subheader("Subsidy Gap Trends Over Time")

# Filter out empty rows to keep the chart clean
plot_df = df.dropna(subset=['ron95_gap', 'diesel_gap'])

if not plot_df.empty:
    fig = px.line(
        plot_df, 
        x="date", 
        y=["ron95_gap", "diesel_gap"],
        labels={"value": "Subsidy Gap (RM / Liter)", "date": "Date", "variable": "Fuel Type"},
        color_discrete_map={
            "ron95_gap": "#F5B041", # Yellow/Orange for RON95
            "diesel_gap": "#3498DB" # Blue for Diesel
        }
    )
    # Customize legend titles
    newnames = {'ron95_gap': 'RON95 Gap', 'diesel_gap': 'Diesel Gap'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough data to plot subsidy gaps yet.")

# 7. Raw Data Table
with st.expander("View Raw Database Records"):
    # Reverse sort to show newest first in the table
    st.dataframe(
        df.sort_values(by="date", ascending=False), 
        use_container_width=True, 
        hide_index=True
    )