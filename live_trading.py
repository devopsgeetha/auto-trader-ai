# live_trading.py
import alpaca_trade_api as tradeapi
import os
import logging

API_KEY = os.getenv("ALPACA_KEY")
API_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

if not API_KEY or not API_SECRET:
    raise ValueError("Missing ALPACA_KEY or ALPACA_SECRET environment variables")

try:
    api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL)
    # Test connection
    api.get_account()
except Exception as e:
    logging.error(f"Failed to initialize Alpaca API: {e}")
    raise

def place_order(symbol, side, qty=1):
    try:
        return api.submit_order(
            symbol=symbol,
            side=side.lower(),
            type="market",
            qty=qty,
            time_in_force="gtc"
        )
    except Exception as e:
        logging.error(f"Failed to place order for {symbol}: {e}")
        raise

def get_live_quote(symbol):
    try:
        quote = api.get_latest_quote(symbol)
        return quote.ask_price
    except Exception as e:
        logging.error(f"Failed to get quote for {symbol}: {e}")
        raise
