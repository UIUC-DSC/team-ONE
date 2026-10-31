import os
import requests
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

API_KEY = os.environ["EIA_API_KEY"]
URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"

def fetch_demand(region="MISO", start="2021-01-01T00", end="2025-12-31T23"):
    rows, offset = [], 0
    while True:
        params = {
            "api_key": API_KEY,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": region,
            "facets[type][]": "D",          # D = demand
            "start": start,
            "end": end,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": 5000,                  # max per request
        }
        r = requests.get(URL, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()["response"]["data"]
        if not data:
            break
        rows.extend(data)
        offset += 5000
    df = pd.DataFrame(rows)
    df["period"] = pd.to_datetime(df["period"], format="%Y-%m-%dT%H")
    df["value"] = pd.to_numeric(df["value"])
    return df[["period", "value"]].set_index("period").sort_index()

df = fetch_demand("MISO")
df.to_csv("miso_demand.csv")   # save so you don't re-download every time
print(df.shape)
print(df.head(100))

missing_value_rows = df["value"].isna().sum()
df = df.dropna(subset=["value"])
print(f"Dropped {missing_value_rows} rows with missing demand values")

# convert UTC to Central time first
df.index = df.index.tz_localize("UTC").tz_convert("America/Chicago")

df["hour"] = df.index.hour                  # 0-23
df["day_of_week"] = df.index.dayofweek      # 0=Monday ... 6=Sunday
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
df["month"] = df.index.month                # 1-12
df["year"] = df.index.year
df["day_of_year"] = df.index.dayofyear      # 1-366

df["hour"] = df.index.hour
df["day_of_week"] = df.index.dayofweek  # Monday=0 through Sunday=6
df["day_name"] = df.index.day_name()
df["is_weekend"] = df.index.dayofweek >= 5
df["month"] = df.index.month
df["year"] = df.index.year

holiday_calendar = USFederalHolidayCalendar()
holiday_dates = holiday_calendar.holidays(
    start=pd.Timestamp(df.index.min().year - 1, 1, 1),
    end=pd.Timestamp(df.index.max().year + 1, 12, 31),
)
local_dates = df.index.tz_localize(None).normalize()
df["is_holiday"] = local_dates.isin(holiday_dates)

df.to_csv("miso_demand_features.csv")