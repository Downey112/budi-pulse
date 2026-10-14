import io
import random
from functools import lru_cache
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATA_URL = "https://storage.data.gov.my/commodities/fuelprice.csv"

REQUIRED_COLS = {"date", "series_type", "diesel", "ron95"}
PRICE_COLS = (
    "ron95",
    "ron97",
    "diesel",
    "ron95_budi95",
    "diesel_budi",
    "diesel_eastmsia",
)

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
)


@lru_cache(maxsize=1)
def get_robust_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=4, pool_maxsize=4)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
    )
    return session


def load_fuel_data(source_url: str = DATA_URL) -> pd.DataFrame:
    session = get_robust_session()
    try:
        response = session.get(source_url, timeout=25)
        response.raise_for_status()
        df = pd.read_csv(io.BytesIO(response.content), low_memory=False)
    except Exception as err:
        raise RuntimeError(f"failed to fetch CSV data: {err}") from err

    if not REQUIRED_COLS.issubset(df.columns):
        missing = REQUIRED_COLS - set(df.columns)
        raise KeyError(f"schema mismatch. missing columns: {missing}")

    df = df.loc[df["series_type"] == "level"].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    existing_price_cols = [c for c in PRICE_COLS if c in df.columns]
    if existing_price_cols:
        df[existing_price_cols] = df[existing_price_cols].apply(pd.to_numeric, errors="coerce")

    return df.sort_values(by="date", ascending=True, ignore_index=True)


def calculate_spreads(df: pd.DataFrame) -> pd.DataFrame:
    spread_df = df.copy()

    if "diesel" in spread_df.columns and "diesel_budi" in spread_df.columns:
        spread_df["diesel_subsidy_delta"] = (
            spread_df["diesel"] - spread_df["diesel_budi"]
        ).clip(lower=0.0)

    if "ron95" in spread_df.columns and "ron95_budi95" in spread_df.columns:
        spread_df["ron95_subsidy_delta"] = (
            spread_df["ron95"] - spread_df["ron95_budi95"]
        ).clip(lower=0.0)

    return spread_df


def _fmt_rm(val, suffix: str = "") -> str:
    if val is None or pd.isna(val):
        return "N/A"
    return f"RM {float(val):.2f}{suffix}"


def get_latest_summary() -> None:
    df = load_fuel_data()
    spreads = calculate_spreads(df)
    if spreads.empty:
        print("[WARN] No weekly price records found.")
        return

    latest = spreads.iloc[-1]
    print(f"[INFO] Ingested {len(spreads)} weekly price records via CSV.")
    print(f"[INFO] Latest record date: {latest['date'].strftime('%Y-%m-%d')}")
    print(f"       RON95 (Market):      {_fmt_rm(latest.get('ron95'))}")
    print(f"       RON95 (BUDI 95):     {_fmt_rm(latest.get('ron95_budi95'))}")
    print(f"       RON95 Subsidy Gap:   {_fmt_rm(latest.get('ron95_subsidy_delta'), '/L')}")
    print(f"       Diesel (Market):     {_fmt_rm(latest.get('diesel'))}")
    print(f"       Diesel (BUDI):       {_fmt_rm(latest.get('diesel_budi'))}")
    print(f"       Diesel Subsidy Gap:  {_fmt_rm(latest.get('diesel_subsidy_delta'), '/L')}")


if __name__ == "__main__":
    get_latest_summary()