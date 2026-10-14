import math
import os
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

try:
    from src.ingest import calculate_spreads, load_fuel_data
except ImportError:
    from ingest import calculate_spreads, load_fuel_data

load_dotenv()

SRC_COLS = (
    "ron95",
    "ron95_budi95",
    "ron95_subsidy_delta",
    "diesel",
    "diesel_budi",
    "diesel_subsidy_delta",
)

BATCH_SIZE = 500


def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("Missing Supabase credentials. Check your .env file.")
    return create_client(url, key)


def clean_value(val: Any) -> Optional[float]:
    if val is None or pd.isna(val):
        return None
    fval = float(val)
    if math.isnan(fval) or math.isinf(fval):
        return None
    return round(fval, 4)


def serialize_records(spreads: pd.DataFrame) -> List[Dict[str, Any]]:
    if spreads.empty:
        return []

    dates_str = pd.to_datetime(spreads["date"]).dt.strftime("%Y-%m-%d").tolist()
    n_rows = len(spreads)
    arrays = []

    for col in SRC_COLS:
        if col in spreads.columns:
            arr = pd.to_numeric(spreads[col], errors="coerce").round(4).to_numpy(dtype=float)
            arrays.append([None if np.isnan(x) or np.isinf(x) else float(x) for x in arr])
        else:
            arrays.append([None] * n_rows)

    return [
        {
            "date": d,
            "ron95_market": r95_m,
            "ron95_budi": r95_b,
            "ron95_gap": r95_g,
            "diesel_market": d_m,
            "diesel_budi": d_b,
            "diesel_gap": d_g,
        }
        for d, r95_m, r95_b, r95_g, d_m, d_b, d_g in zip(dates_str, *arrays)
    ]


def upload_to_supabase(client: Optional[Client] = None) -> int:
    supabase = client or get_supabase_client()
    df = load_fuel_data()
    spreads = calculate_spreads(df)
    records = serialize_records(spreads)

    if not records:
        print("[WARN] No records to upsert.")
        return 0

    print(f"[INFO] Upserting {len(records)} records to Supabase...")
    table = supabase.table("fuel_subsidy_records")
    for start in range(0, len(records), BATCH_SIZE):
        chunk = records[start : start + BATCH_SIZE]
        table.upsert(chunk, on_conflict="date").execute()

    print("[SUCCESS] Data successfully pushed to database.")
    return len(records)


if __name__ == "__main__":
    upload_to_supabase()