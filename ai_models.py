# ai_models.py
import pandas as pd
import numpy as np

def add_direction_prediction(df: pd.DataFrame, price_col: str) -> pd.DataFrame:
    """
    Stub for AI model.
    For now, use a very simple heuristic:
      - if short SMA > long SMA -> predict UP
      - else predict DOWN
    Later you can replace this with a real LSTM/Transformer.
    """
    df = df.copy()

    if "sma_short" not in df.columns or "sma_long" not in df.columns:
        return df  # nothing to do

    df["pred_up_prob"] = 0.5  # neutral baseline

    bullish = df["sma_short"] > df["sma_long"]
    df.loc[bullish, "pred_up_prob"] = 0.7
    df.loc[~bullish, "pred_up_prob"] = 0.3

    df["pred_signal"] = np.where(df["pred_up_prob"] >= 0.55, "BUY", "SELL")

    return df
