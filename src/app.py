import os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="BudiPulse • Malaysia", page_icon="🇲🇾", layout="wide")

load_dotenv()

# ==========================================
# 2. Database Connection (STAYS THE SAME)
# ==========================================
@st.cache_resource
def init_connection() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        st.error("Missing Supabase credentials. Check your .env file.")
        st.stop()
    return create_client(url, key)

supabase = init_connection()

# ==========================================
# 3. Custom CSS - The Industry Polish
# ==========================================
# We use custom CSS to force premium card designs, fonts, and round borders.
st.markdown("""
<style>
    /* Remove redundant padding at top */
    .block-container { padding-top: 1.5rem !important; }
    
    /* Global Font Tweak */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Target the sidebar directly to prevent content shifting */
    [data-testid="stSidebar"] {
        padding-top: 0px !important;
    }

    /* PREMIER METRIC CARDS - CSS styling */
    .metric-card {
        background-color: #262730;
        border-radius: 12px;
        padding: 24px;
        position: relative;
        border: 1px solid #333;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.4);
        border-color: #F5B041;
    }
    .metric-label {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #888;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 38px;
        font-weight: 800;
        color: #FAFAFA;
        line-height: 1.1;
    }
    .metric-delta {
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
    }
    .metric-icon {
        position: absolute;
        bottom: -20px;
        right: -10px;
        font-size: 100px;
        color: rgba(255, 255, 255, 0.03);
    }
    .glow-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at top left, rgba(245, 176, 65, 0.05), transparent 60%);
    }

    /* Header Styling */
    h1 { font-weight: 800 !important; color: #FAFAFA !important; }
    h2 { font-weight: 700 !important; margin-top: 2rem !important; }
    
    /* Cleaner Table Styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #333 !important;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. Data Ingestion & Transformation
# ==========================================
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    response = supabase.table("fuel_subsidy_records").select("*").execute()
    df = pd.DataFrame(response.data)
    if df.empty: return df
    df["date"] = pd.to_datetime(df["date"])
    # Sort chronologically for charting
    return df.sort_values(by="date", ascending=True).reset_index(drop=True)

# ==========================================
# 5. App Layout & Sidebar (Updated)
# ==========================================
st.sidebar.markdown("<br>", unsafe_allow_html=True)
# Updated Flag source that won't be blocked
st.sidebar.image("https://flagcdn.com/w160/my.png", width=90)
st.sidebar.title("BudiPulse")
st.sidebar.markdown("Data Governance & Subsidy Tracker")
st.sidebar.write("") 

with st.spinner("Initializing system connection..."):
    df = load_data()

if df.empty:
    st.warning("No data found in the production schema.")
    st.stop()

# Date Filter Widget
st.sidebar.subheader("Timeframe Analysis")
timeframe = st.sidebar.radio(
    "Select analysis range:",
    ["All Time", "Last 6 Months", "Last 3 Months"],
    index=1
)

# Apply Filter logic
if timeframe == "Last 6 Months":
    cutoff = datetime.now() - pd.DateOffset(months=6)
    filtered_df = df[df["date"] >= cutoff]
elif timeframe == "Last 3 Months":
    cutoff = datetime.now() - pd.DateOffset(months=3)
    filtered_df = df[df["date"] >= cutoff]
else:
    filtered_df = df

st.sidebar.write("")
st.sidebar.divider()
st.sidebar.markdown(
    "<span style='color: #666; font-size: 12px;'>Pipeline Status:</span> <span style='color: #2ECC71; font-weight:700;'>LIVE</span>", 
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<span style='color: #666; font-size: 12px;'>Automated Update:</span> <span style='color: #FAFAFA;'>Weekly (Wed 00:00 UTC)</span>", 
    unsafe_allow_html=True
)

# ==========================================
# 6. Main Dashboard Area
# ==========================================

# Use wide columns to structure the page better
left_co, right_co = st.columns([6, 1], gap="medium")
with left_co:
    # Adding a badge effect to the title
    st.markdown("""
        <h1>BudiPulse <span style='color: #F5B041; font-size: 20px; font-weight: 400; vertical-align: middle; margin-left:10px; border: 1px solid #333; padding: 4px 12px; border-radius: 50px; background-color: #262730;'>PRODUCTION LIVE</span></h1>
    """, unsafe_allow_html=True)
    st.markdown("Automated Data Pipeline Tracking Malaysia's Fuel Subsidy Rationalization (BUDI MADANI Fiscal Gaps)")
with right_co:
    st.write("") # Spacer to push the flag up

st.write("") # Vertical spacer before metrics

# ==========================================
# 7. Prepremier Metric Cards Row (Visual Engagement)
# ==========================================
# Instead of standard st.metric, we define custom HTML/CSS to make glowing, icon-driven cards.
latest = df.iloc[-1]
# We MUST use the UNFILTERED data to find the true previous week
# Locate the actual position of the latest week in the full dataframe
latest_idx = df.index[-1]
# If we have at least 2 weeks of history, get the previous week
prev = df.iloc[latest_idx - 1] if latest_idx >= 1 else latest

latest_date = latest['date'].strftime('%d %B %Y')

st.markdown(f"📊 **Market Pricing Status:** As of `{latest_date}` (Week-over-Week volatility tracker)")
st.write("") # Vertical spacer

# Calculate weekly differences (Deltas)
ron95_delta_gap = latest['ron95_gap'] - prev['ron95_gap']
diesel_delta_gap = latest['diesel_gap'] - prev['diesel_gap']

# Define HTML for the two key metrics (RON95 and Diesel Gaps)
# Metric 1: RON95 Gap
ron95_delta_class = "color: #ff4b4b;" if ron95_delta_gap > 0 else "color: #2ecc71;"
ron95_arrow = "↑" if ron95_delta_gap > 0 else "↓"

metric_card_ron95 = f"""
    <div class="metric-card">
        <div class="glow-overlay"></div>
        <div class="metric-label">RON95 Subsidy Gap</div>
        <div class="metric-value">RM {latest['ron95_gap']:.2f}</div>
        <div class="metric-delta" style="{ron95_delta_class}">
            {ron95_arrow} {abs(ron95_delta_gap):.2f} <span style="color: #666; margin-left:2px;">vs. last week</span>
        </div>
        <div class="metric-icon">⛽</div>
    </div>
"""

# Metric 2: Diesel Gap
diesel_delta_class = "color: #ff4b4b;" if diesel_delta_gap > 0 else "color: #2ecc71;"
diesel_arrow = "↑" if diesel_delta_gap > 0 else "↓"

metric_card_diesel = f"""
    <div class="metric-card">
        <div class="glow-overlay"></div>
        <div class="metric-label">Diesel Subsidy Gap</div>
        <div class="metric-value">RM {latest['diesel_gap']:.2f}</div>
        <div class="metric-delta" style="{diesel_delta_class}">
            {diesel_arrow} {abs(diesel_delta_gap):.2f} <span style="color: #666; margin-left:2px;">vs. last week</span>
        </div>
        <div class="metric-icon">🚚</div>
    </div>
"""

# Render the cards using columns
mCol1, mCol2 = st.columns(2, gap="large")
with mCol1:
    st.markdown(metric_card_ron95, unsafe_allow_html=True)
with mCol2:
    st.markdown(metric_card_diesel, unsafe_allow_html=True)

st.write("") # Vertical spacer before chart

# ==========================================
# 8. Optimized Visualization (Industry Style)
# ==========================================
st.markdown("---")
st.subheader("Subsidy Gap Trends Over Time")

plot_df = filtered_df.dropna(subset=['ron95_gap', 'diesel_gap'])

if not plot_df.empty:
    # Use Plotly Express for industry standard interactive charts
    fig = px.line(
        plot_df, 
        x="date", 
        y=["ron95_gap", "diesel_gap"],
        color_discrete_map={
            "ron95_gap": "#F5B041", # Primary vibrant yellow-orange
            "diesel_gap": "#3498DB"  # Contrasting clean blue
        }
    )
    
    # ADVANCED PLOTLY STYLING (The industry look)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", # Transparent background
        paper_bgcolor="rgba(0,0,0,0)", # Transparent background
        xaxis_title="", # Remove redundant X title (we know it's Date)
        yaxis_title="Subsidy Gap (RM / Liter)",
        legend_title_text="",
        font=dict(family="Inter, sans-serif", color="#888"), # Unified font
        # Horizontal legend placed elegantly at top-right
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified", # Single hover label across both lines
        margin=dict(l=0, r=10, t=30, b=0) # Minimal padding
    )
    
    # Custom hover template polish
    fig.update_traces(hovertemplate="RM %{y:.2f} <extra></extra>")
    
    # Fine-tune the axes gridlines for a clean look
    fig.update_xaxes(
        showgrid=False, 
        linecolor="#333", 
        tickformat="%b %Y", # Example: 'Aug 2026'
        tickfont=dict(color="#666")
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor="#333333", 
        linecolor="rgba(0,0,0,0)",
        tickprefix="RM ",
        tickfont=dict(color="#666")
    )
    
    # Clean up trace names to proper capitalized labels
    newnames = {'ron95_gap': 'RON95 Gap', 'diesel_gap': 'Diesel Gap'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    
    # Draw chart with the default Plotly toolbar REMOVED to keep it clean
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Insufficient longitudinal data to plot subsidy gap trends for this timeframe.")

# ==========================================
# 9. Curated Data Table (Clean Governance)
# ==========================================
st.write("")
st.write("")
st.subheader("Data Governance Schema")

# Instead of default table, we hide index and round floats for cleaner display
governance_df = filtered_df.sort_values(by="date", ascending=False).reset_index(drop=True)
# Apply a slight background color to highlight the 'Gap' columns (the purpose of the table)
def highlight_gaps(s):
    if s.name in ['ron95_gap', 'diesel_gap']:
        return ['background-color: rgba(245, 176, 65, 0.03)'] * len(s)
    return [''] * len(s)

styled_table = governance_df.style\
    .format({'ron95_market': '{:.2f}', 'ron95_gap': '{:.2f}', 'diesel_market': '{:.2f}', 'diesel_gap': '{:.2f}'})\
    .apply(highlight_gaps, axis=0)

# Display table inside an expander so it doesn't clutter the main view
with st.expander("🔍 View Validated Raw Schema Records", expanded=False):
    st.dataframe(
        styled_table, 
        use_container_width=True, 
        hide_index=True
    )
    st.markdown("<span style='color: #555; font-size: 12px;'>Data Source: Calculated from validated OpenDOSM endpoints. Duplicate checking enforced via .upsert() primary key governance.</span>", unsafe_allow_html=True)