import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

def fetch_income_data():
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": "B19013_001E,NAME",
        "for": "zip code tabulation area:*",
        "key": CENSUS_API_KEY
        
    }
    r = requests.get(url, params=params)
    print("Status code:", r.status_code)
    r.raise_for_status()
    df = pd.DataFrame(r.json()[1:], columns=r.json()[0])
    df = df.rename(columns={"B19013_001E": "median_income", "zip code tabulation area": "zcta"})
    return df

if __name__ == "__main__":
    df = fetch_income_data()
    df.to_csv("data/all_zcta_income.csv", index=False)
    print(f"Loaded {len(df)} ZCTA rows nationwide")
    print(df.head())