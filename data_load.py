
import requests
import pandas as pd
import duckdb

def fetch_311_data():
    url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    params = {
        "$where": "created_date >= '2022-01-01'",
        "$limit": 50000,
        "$select": "unique_key,created_date,closed_date,complaint_type,incident_zip,borough"
    }
    r = requests.get(url, params=params)
    return pd.DataFrame(r.json())

def load_into_duckdb(df, db_path="nyc311.db"):
    con = duckdb.connect(db_path)
    con.execute("CREATE OR REPLACE TABLE requests AS SELECT * FROM df")
    con.close()

if __name__ == "__main__":
    df = fetch_311_data()
    df.to_csv("data/311_sample.csv", index=False)
    load_into_duckdb(df)
    print(f"Loaded {len(df)} rows into nyc311.db")
