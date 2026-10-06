# CLAUDE.md - budi-pulse Guidelines

## Environment & Virtual Environment
- Python virtual environment is located in `venv/`.
- Activate in Git Bash: `source venv/Scripts/activate`
- Run tools directly with the venv interpreter if unactivated: `venv/Scripts/python -m ...`

## Development & Test Commands
- Install packages: `pip install -r requirements.txt`
- Run dashboard: `python -m streamlit run src/app.py`
- Preview ingest (read-only, prints the latest prices): `python src/ingest.py`
- Run ETL pipeline: `python src/db.py` — this upserts into the production Supabase table, so confirm before running it.
- Tests: there is no `tests/` directory and `pytest` is not installed. Smoke-test the dashboard headlessly with `streamlit.testing.v1.AppTest` against `src/app.py`.
- Check syntax: `python -m py_compile src/*.py`
- Credentials: `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are read from `.env` in the repo root (never commit it).

## Repository Structure & Rules
- Core application code lives in `src/`: `ingest.py` (fetch + transform), `db.py` (upsert to Supabase), `app.py` (Streamlit dashboard).
- Never modify or commit files inside `venv/`.
- If new packages are introduced, update `requirements.txt`.
- Handle missing files, missing environment variables, and null values gracefully.

## Debugging Workflow
1. Trace the stack trace or failure back to the exact file in `src/`.
2. Apply targeted fixes without rewriting unrelated code.
3. Re-run the affected script or an `AppTest` run of the dashboard to confirm the error is gone.
