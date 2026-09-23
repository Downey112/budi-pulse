# BudiPulse 🇲🇾

[![Live Dashboard](https://img.shields.io/badge/Streamlit-Live_Production-FF4B4B?style=for-the-badge&logo=streamlit)](https://budi-pulse.streamlit.app)
[![ETL Status](https://img.shields.io/badge/Pipeline-Active-2ECC71?style=for-the-badge)](https://github.com/downey112/budi-pulse/actions)
[![Database](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)

An automated, end-to-end data engineering pipeline and interactive dashboard tracking Malaysia's BUDI MADANI fuel subsidy rationalization and fiscal gaps.

**Live Dashboard:** [budi-pulse.streamlit.app](https://budi-pulse.streamlit.app)

---

## 📖 Project Overview
BudiPulse bridges the gap between macroeconomic government datasets and personal financial impact. It automatically tracks the weekly spread between market float prices and BUDI MADANI retail caps (RON95 and Diesel), visualizing the fiscal burden absorbed by the Malaysian government. 

The dashboard features a **Personal Commute Burden Calculator**, allowing end-users to input their daily mileage and vehicle efficiency to dynamically calculate their monthly fuel cost exposure against the 200-liter subsidized quota.

## 🏗️ Architecture & Tech Stack
This project utilizes a modern cloud data stack with a fully automated, zero-cost infrastructure:

* **Data Source (Extraction):** OpenDOSM (Department of Statistics Malaysia) Parquet/CSV endpoints.
* **Transformation (Python):** `pandas` and `requests`, utilizing robust HTTP sessions with automated retries and randomized user-agents to bypass government CDN/WAF blocks.
* **Database (Storage & Governance):** Supabase (PostgreSQL). Employs primary key constraints and `.upsert()` logic to prevent duplicate records and ensure data integrity.
* **Cloud Orchestration (CI/CD):** GitHub Actions triggers a cron job every Sunday and Wednesday at 00:00 UTC to scrape, transform, and load the latest weekly pricing data.
* **Frontend (Visualization):** Streamlit Community Cloud & Plotly. Features custom CSS for glowing metric cards, responsive layout spacing, and a unified dark theme.

### Infrastructure Health-Check
To prevent the Streamlit application from entering its default 7-day hibernation state, the GitHub Actions ETL pipeline is configured with a final step that executes an automated `curl` ping against the live URL. This guarantees 100% frontend uptime and instant load speeds for stakeholders.

---

## ⚙️ Local Development Setup

To run the pipeline and dashboard on your local machine:

**1. Clone the repository**
```bash
git clone [https://github.com/downey112/budi-pulse.git](https://github.com/downey112/budi-pulse.git)
cd budi-pulse
```

**2. Set up the virtual environment & install dependencies**
```bash
python -m venv .venv
source .venv/Scripts/activate  # On Windows Git Bash
pip install -r requirements.txt
```

**3. Configure Environment Variables**
Create a `.env` file in the root directory and add your Supabase credentials:
```toml
SUPABASE_URL="your_supabase_project_url"
SUPABASE_SERVICE_ROLE_KEY="your_supabase_master_key"
```

**4. Run the ETL Pipeline manually**
```bash
python src/db.py
```

**5. Launch the Streamlit Dashboard**
```bash
python -m streamlit run src/app.py
```
