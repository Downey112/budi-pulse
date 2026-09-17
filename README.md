\# BudiPulse 🇲🇾



An automated, end-to-end data engineering pipeline and interactive dashboard tracking Malaysia's BUDI MADANI fuel subsidy rationalization and fiscal gaps.



\*\*Live Dashboard:\*\* \[View the App](https://budi-pulse.streamlit.app/)



\## Architecture

\* \*\*Data Source:\*\* OpenDOSM (Department of Statistics Malaysia) Parquet/CSV endpoints.

\* \*\*Extraction \& Transformation:\*\* Python (`pandas`, `requests`) utilizing robust HTTP sessions with automated retries and randomized user-agents to bypass government CDN/WAF blocks.

\* \*\*Orchestration:\*\* GitHub Actions triggers a cron job every Wednesday at 00:00 UTC to scrape, transform, and load the latest weekly pricing data.

\* \*\*Database:\*\* Supabase (PostgreSQL) handles data storage and prevents duplicate entries using `.upsert()`.

\* \*\*Frontend:\*\* Streamlit and Plotly serve the interactive, live-updating dashboard directly from the database.



\## Local Setup

1\. Clone the repository.

2\. Install requirements: `pip install -r requirements.txt`

3\. Create a `.env` file with `SUPABASE\_URL` and `SUPABASE\_SERVICE\_ROLE\_KEY`.

4\. Run the ETL pipeline: `python src/db.py`

5\. Launch the dashboard: `streamlit run src/app.py`

