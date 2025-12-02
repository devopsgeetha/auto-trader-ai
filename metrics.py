# metrics.py
import numpy as np
import pandas as pd

def compute_performance_stats(df, price_col, risk_free_rate=0.03):
    df = df.copy()
    
    # Validate required columns
    required_cols = ["equity_curve", "date", "strategy_returns_net", "position"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    # Strategy equity curve
    equity = df["equity_curve"]

    # Total Return
    total_return = equity.iloc[-1] - 1

    # CAGR (Annualized Return)
    days = (df["date"].iloc[-1] - df["date"].iloc[0]).days
    cagr = (equity.iloc[-1]) ** (365 / days) - 1 if days > 0 else np.nan

    # Daily returns
    daily_ret = df["strategy_returns_net"].dropna()

    # Sharpe Ratio
    sharpe = (daily_ret.mean() - risk_free_rate / 252) / (daily_ret.std() + 1e-9)
    sharpe = sharpe * np.sqrt(252)

    # Max Drawdown
    roll_max = equity.cummax()
    dd = equity / roll_max - 1
    max_dd = dd.min()

    # Trade stats
    trades = df[df["position"].diff() != 0]
    wins = trades[trades["strategy_returns_net"] > 0]
    losses = trades[trades["strategy_returns_net"] <= 0]
    win_rate = len(wins) / max(len(trades), 1)
    losses_sum = abs(losses["strategy_returns_net"].sum())
    profit_factor = wins["strategy_returns_net"].sum() / max(losses_sum, 1e-9) if losses_sum > 0 else np.inf

    return {
        "total_return": total_return,
        "CAGR": cagr,
        "Sharpe": sharpe,
        "MaxDD": max_dd,
        "WinRate": win_rate,
        "ProfitFactor": profit_factor,
        "Trades": len(trades),
    }
