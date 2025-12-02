import os
import pandas as pd
from alpha_vantage.timeseries import TimeSeries

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

if not API_KEY:
    # Try a fallback or provide a more helpful error message
    print("⚠️  ALPHAVANTAGE_API_KEY not found in environment variables.")
    print("💡 Solutions:")
    print("   1. Restart your terminal after running 'setx ALPHAVANTAGE_API_KEY your_key'")
    print("   2. Set in current session: $env:ALPHAVANTAGE_API_KEY = 'your_key'")
    print("   3. Create a .env file with ALPHAVANTAGE_API_KEY=your_key")
    raise ValueError("❌ Missing AlphaVantage API key. Set ALPHAVANTAGE_API_KEY first.")

def get_price_history(ticker: str, period: str = "3mo") -> pd.DataFrame:
    ts = TimeSeries(key=API_KEY, output_format='pandas')

    # Map UI period → AV function options
    if period in ["3mo", "6mo"]:
        data, meta = ts.get_daily(symbol=ticker, outputsize='compact')
    else:
        data, meta = ts.get_daily(symbol=ticker, outputsize='full')

    df = data.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume",
    })

    df.index = pd.to_datetime(df.index)
    df = df.sort_index().reset_index().rename(columns={"index": "date"})

    # Limit range manually for UI periods
    if period == "3mo":
        df = df.tail(60)  # ~3 months
    elif period == "6mo":
        df = df.tail(120)

    return df
