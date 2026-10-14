# BudiPulse

[![Live Dashboard](https://img.shields.io/badge/Streamlit-Live_Production-E5A000?style=flat-square&logo=streamlit)](https://budi-pulse.streamlit.app)
[![ETL Status](https://img.shields.io/badge/Pipeline-Active-10B981?style=flat-square)](https://github.com/downey112/budi-pulse/actions)
[![Database](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com/)

End-to-end data pipeline and minimalist telemetry dashboard tracking Malaysia's BUDI MADANI fuel subsidy spreads and monthly household quota exposure.

**Live Dashboard:** [budi-pulse.streamlit.app](https://budi-pulse.streamlit.app)

## Overview
BudiPulse tracks the weekly spread between unsubsidized market float prices and BUDI MADANI retail caps for RON95 and Diesel using official OpenDOSM datasets.

Includes a **Commute Quota Calculator** (`@st.fragment` isolated) to estimate monthly fuel spend and unsubsidized market exposure against the 300 L standard quota (400 L for qualifying pickups / 4WDs).

## Stack
* **Source:** OpenDOSM (`https://storage.data.gov.my/commodities/fuelprice.csv`)
* **Ingestion (`src/ingest.py`):** Cached `requests.Session` with retry backoff, `BytesIO` zero-copy CSV parsing, and vectorized numeric coercion.
* **Storage (`src/db.py`):** Supabase (PostgreSQL) with vectorized record serialization and chunked `.upsert(..., on_conflict="date")`.
* **CI/CD (`.github/workflows/`):** Scheduled GitHub Actions (`pipeline.yml` every Sun/Wed 00:00 UTC; `keep_alive.yml` headless Playwright wake check every 6 hours).
* **Dashboard (`src/app.py`):** Streamlit + Plotly with tabular monospace typography, subtle CSS motion (`prefers-reduced-motion` compliant), `@st.fragment` partial reruns, and native `st.column_config` grid rendering.

## Local Setup

```bash
git clone https://github.com/downey112/budi-pulse.git
cd budi-pulse
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Create `.env` in the repo root:
```env
SUPABASE_URL="your_supabase_project_url"
SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_role_key"
SUPABASE_ANON_KEY="your_supabase_anon_key"
```

## Commands

```bash
# Preview ingestion (read-only)
python src/ingest.py

# Run ETL upsert to Supabase
python src/db.py

# Run unit & integration test suite
python -m unittest discover -s tests -v

# Start dashboard
python -m streamlit run src/app.py
```
