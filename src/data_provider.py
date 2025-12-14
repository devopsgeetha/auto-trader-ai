# data_provider.py

import requests
import pandas as pd
import time

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_price_history(ticker, period="3mo", retries=3):
    params = {}

    if period.endswith("mo"):
        params["range"] = period
    else:
        params["period1"] = "0"
        params["period2"] = str(int(time.time()))

    params["interval"] = "1d"

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(BASE_URL.format(ticker), params=params, headers=HEADERS, timeout=10)

            if resp.status_code != 200:
                print(f"HTTP {resp.status_code} for {ticker} (attempt {attempt}/{retries})")
                time.sleep(attempt)
                continue

            data = resp.json()
            result = data.get("chart", {}).get("result", None)

            if not result:
                print(f"⚠️ No chart result for {ticker} (attempt {attempt}/{retries})")
                time.sleep(attempt)
                continue

            res = result[0]
            timestamps = res.get("timestamp", [])
            if not timestamps:
                print(f"⚠️ No timestamps for {ticker} (attempt {attempt}/{retries})")
                time.sleep(attempt)
                continue

            prices = res["indicators"]["quote"][0]

            df = pd.DataFrame({
                "date": pd.to_datetime(timestamps, unit="s"),
                "open": prices.get("open", []),
                "high": prices.get("high", []),
                "low": prices.get("low", []),
                "close": prices.get("close", []),
                "volume": prices.get("volume", []),
            })

            df.dropna(inplace=True)
            df.sort_values("date", inplace=True)
            df.reset_index(drop=True, inplace=True)

            return df

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e} (attempt {attempt}/{retries})")
            time.sleep(attempt)

    print(f"🚫 Final failure fetching {ticker}")
    return pd.DataFrame()
