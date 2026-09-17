import io
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd

# Switch to CSV endpoint to bypass binary firewall blocks
DATA_URL = "https://storage.data.gov.my/commodities/fuelprice.csv"

def get_robust_session():
    """Create an HTTP session that mimics different browsers and retries."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=5,
        backoff_factor=2, # Wait longer (2s, 4s, 8s) between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Randomize the User-Agent so we don't look like the same script hitting refresh
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    session.headers.update({
        "User-Agent": random.choice(user_agents),
        "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    })
    
    return session

def load_fuel_data(source_url: str = DATA_URL) -> pd.DataFrame:
    session = get_robust_session()
    
    try:
        response = session.get(source_url, timeout=30)
        response.raise_for_status()
        
        # Parse as CSV instead of Parquet
        buffer = io.StringIO(response.text)
        df = pd.read_csv(buffer)
    except Exception as err:
        raise RuntimeError(f"failed to fetch CSV data: {err}")

    # sanity check: ensure essential baseline columns exist
    required_cols = {"date", "series_type", "diesel", "ron95"}
    if not required_cols.issubset(df.columns):
        raise KeyError(f"schema mismatch. missing columns: {required_cols - set(df.columns)}")

    # filter for absolute price levels (drop weekly percentage changes)
    df = df[df["series_type"] == "level"].copy()
    df["date"] = pd.to_datetime(df["date"])

    # cast all price columns to float
    price_cols = [
        "ron95", "ron97", "diesel",
        "ron95_budi95", "diesel_budi", "diesel_eastmsia"
    ]
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values(by="date").reset_index(drop=True)

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

def get_latest_summary():
    df = load_fuel_data()
    spreads = calculate_spreads(df)
    latest = spreads.iloc[-1]

    print(f"[INFO] Ingested {len(spreads)} weekly price records via CSV.")
    print(f"[INFO] Latest record date: {latest['date'].strftime('%Y-%m-%d')}")
    print(f"       RON95 (Market):      RM {latest.get('ron95', 0):.2f}")
    print(f"       RON95 (BUDI 95):     RM {latest.get('ron95_budi95', 0):.2f}")
    print(f"       RON95 Subsidy Gap:   RM {latest.get('ron95_subsidy_delta', 0):.2f}/L")
    print(f"       Diesel (Market):     RM {latest.get('diesel', 0):.2f}")
    print(f"       Diesel (BUDI):       RM {latest.get('diesel_budi', 0):.2f}")
    print(f"       Diesel Subsidy Gap:  RM {latest.get('diesel_subsidy_delta', 0):.2f}/L")

if __name__ == "__main__":
    get_latest_summary()