import os
import math
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from ingest import load_fuel_data, calculate_spreads

# Load credentials from the hidden .env file
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_value(val):
    """Convert pandas NaN/NaT to None for PostgreSQL JSON compatibility."""
    if pd.isna(val) or math.isnan(val):
        return None
    return float(val)

def upload_to_supabase():
    df = load_fuel_data()
    spreads = calculate_spreads(df)
    
    # Convert dates to strings for JSON serialization
    spreads["date"] = spreads["date"].dt.strftime("%Y-%m-%d")
    
    records = []
    for _, row in spreads.iterrows():
        record = {
            "date": row["date"],
            "ron95_market": clean_value(row.get("ron95")),
            "ron95_budi": clean_value(row.get("ron95_budi95")),
            "ron95_gap": clean_value(row.get("ron95_subsidy_delta")),
            "diesel_market": clean_value(row.get("diesel")),
            "diesel_budi": clean_value(row.get("diesel_budi")),
            "diesel_gap": clean_value(row.get("diesel_subsidy_delta"))
        }
        records.append(record)

    print(f"[INFO] Upserting {len(records)} records to Supabase...")
    
    # .upsert() updates the row if the date already exists, preventing duplicates
    response = supabase.table("fuel_subsidy_records").upsert(records).execute()
    
    print("[SUCCESS] Data successfully pushed to database.")

if __name__ == "__main__":
    upload_to_supabase()