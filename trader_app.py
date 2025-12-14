# trader_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce

from data_provider import get_price_history
from strategy import apply_sma_crossover
from ai_models import add_direction_prediction

# Must be first Streamlit command
st.set_page_config(page_title="Auto-Trading AI (Paper)", page_icon="📈")

st.title("📈 Auto-Trading AI — Multi-Ticker Strategy")
st.write("_Paper-trading demo — no real orders are sent._")

# -------------------------------------------------
# BASIC CONTROLS
# -------------------------------------------------
LISTED_TICKERS = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA"]

col_preset, col_custom = st.columns([2, 1])
with col_preset:
    selected_tickers = st.multiselect("Select preset ticker(s)", LISTED_TICKERS, default=["AAPL"])

with col_custom:
    custom_ticker_input = st.text_input(
        "Add custom ticker(s)", 
        placeholder="e.g., META, NFLX",
        help="Enter ticker symbols separated by commas"
    )

# Combine preset and custom tickers
tickers = list(selected_tickers)
if custom_ticker_input:
    custom_tickers = [t.strip().upper() for t in custom_ticker_input.split(",") if t.strip()]
    tickers.extend(custom_tickers)

# Remove duplicates while preserving order
seen = set()
tickers = [x for x in tickers if not (x in seen or seen.add(x))]

period = st.selectbox("Data period", ["3mo", "6mo", "1y", "2y"], index=1)
short_window = st.slider("Short SMA window", 5, 30, value=10)
long_window = st.slider("Long SMA window", 20, 100, value=30)

# -------------------------------------------------
# ADVANCED CONTROLS
# -------------------------------------------------
st.subheader("⚙️ Strategy Controls")

col1, col2 = st.columns(2)

with col1:
    use_rsi_macd = st.checkbox("Require RSI + MACD confirmation", value=True)
    rsi_window = st.slider("RSI window", 7, 21, value=14)

with col2:
    use_vol_filter = st.checkbox("Apply volatility filter", value=False)
    vol_window = st.slider("Volatility lookback (days)", 5, 60, value=20)
    max_vol_pct = (
        st.slider("Max daily volatility (%)", 1.0, 10.0, value=5.0, step=0.5)
        if use_vol_filter
        else None
    )

use_ai = st.checkbox("Enable AI direction prediction", value=False)

st.subheader("🔐 Risk Management")

use_risk = st.checkbox("Enable Stop-Loss / Take-Profit", value=True)

stop_loss_pct = st.number_input(
    "Stop-Loss (%)", min_value=1.0, max_value=30.0, value=5.0, step=0.5
)

take_profit_pct = st.number_input(
    "Take-Profit (%)", min_value=1.0, max_value=50.0, value=10.0, step=0.5
)

st.subheader("💰 Portfolio & Costs")

col3, col4 = st.columns(2)

with col3:
    portfolio_capital = st.number_input(
        "Total portfolio capital (USD)", min_value=1000, value=10_000, step=1000
    )

with col4:
    trade_cost_bps = st.slider(
        "Per-trade cost (bps)", min_value=0, max_value=50, value=10, step=1
    )

# -------------------------------------------------
# HELPERS
# -------------------------------------------------


def preprocess_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Column normalization BEFORE indexing
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join([str(c).lower() for c in col if c]) for col in df.columns]
    else:
        df.columns = [str(c).lower() for c in df.columns]

    # Detect correct date column (Yahoo = 'date' after lowering)
    date_cols = [c for c in df.columns if c.startswith("date")]
    if not date_cols:
        raise KeyError("No date column found in DataFrame")

    df.rename(columns={date_cols[0]: "date"}, inplace=True)

    # Proper datetime conversion — FIXES 1970 issue permanently
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True).dt.tz_localize(None)

    df = df.dropna(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Detect close column
    close_cols = [c for c in df.columns if "close" in c]
    if not close_cols:
        raise KeyError("No close price column")
    df["close"] = df[close_cols[0]].astype(float)

    return df


def add_display_enhancements(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    emoji = {"BUY": "🟢 BUY", "SELL": "🔴 SELL", "HOLD": "🟡 HOLD", "SL": "🛑 STOP-LOSS", "TP": "🎯 TAKE-PROFIT"}
    df["signal_display"] = df["signal"].map(emoji).fillna("⚪")
    df["date_display"] = df["date"].dt.strftime("%m-%d-%Y")
    return df


def calculate_metrics(df: pd.DataFrame, price_col: str):
    total_return_strategy = df["equity_curve"].iloc[-1] - 1
    total_return_bh = df[price_col].iloc[-1] / df[price_col].iloc[0] - 1

    trades = df[df["position"].diff() != 0]
    wins = trades[trades["strategy_returns_net"] > 0]
    win_rate = (len(wins) / len(trades) * 100) if len(trades) > 0 else 0.0

    return total_return_strategy, total_return_bh, win_rate, len(trades)


# -------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------

results = {}

if st.button("Run Strategy"):
    if not tickers:
        st.warning("Please select at least one ticker.")
    else:
        for ticker in tickers:
            st.header(f"📌 {ticker}")

            raw_df = get_price_history(ticker, period)
            if raw_df is None or raw_df.empty:
                st.error(f"No data returned for {ticker}")
                continue

            # Normalize OHLC and get clean 'date' + 'close'
            try:
                df = preprocess_ohlc(raw_df)
            except KeyError as e:
                st.error(f"{ticker}: {e}")
                continue

            # Apply strategy with indicators & trade costs
            try:
                df, price_col = apply_sma_crossover(
                    df,
                    short_window=short_window,
                    long_window=long_window,
                    use_rsi_macd=use_rsi_macd,
                    rsi_window=rsi_window,
                    use_vol_filter=use_vol_filter,
                    vol_window=vol_window,
                    max_vol_pct=max_vol_pct,
                    trade_cost_bps=trade_cost_bps,
                    stop_loss_pct=stop_loss_pct,
                    take_profit_pct=take_profit_pct,
                    use_risk=use_risk,
                )
            except KeyError as e:
                st.error(f"{ticker}: Missing needed columns: {e}")
                continue
            
            # Apply AI model for direction prediction
            if use_ai:
                df = add_direction_prediction(df, price_col)
                # Display AI prediction
                last = df.iloc[-1]
                st.info(
                    f"🤖 AI prediction: **{last['pred_signal']}** "
                    f"(P(up)={last['pred_up_prob']:.2f}) for next bar."
                )

            # Baseline buy & hold equity curve
            df["bh_equity"] = (df[price_col] / df[price_col].iloc[0]).fillna(1.0)

            # Add emoji display + formatted date
            df = add_display_enhancements(df)

            # Store for portfolio aggregation later
            results[ticker] = (df, price_col)

            # -------------------------------------------------
            # 🔹 TABS UI
            # -------------------------------------------------
            chart_tab, perf_tab, indicator_tab, signals_tab = st.tabs(
                ["📈 Chart", "📊 Performance", "📐 Indicators", "📅 Signals"]
            )

            # 📈 Chart Tab
            with chart_tab:
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(df["date"], df[price_col], label="Close", linewidth=1.5, color="#2E86AB")
                ax.plot(df["date"], df["sma_short"], linestyle="--", label=f"SMA {short_window}", linewidth=1.2, color="#A23B72")
                ax.plot(df["date"], df["sma_long"], linestyle="--", label=f"SMA {long_window}", linewidth=1.2, color="#F18F01")

                # Plot signal markers
                buy = df[df["signal"] == "BUY"]
                sell = df[df["signal"] == "SELL"]
                ax.scatter(buy["date"], buy[price_col], marker="^", color="green", s=100, label="BUY", zorder=5)
                ax.scatter(sell["date"], sell[price_col], marker="v", color="red", s=100, label="SELL", zorder=5)

                ax.set_title(f"{ticker} Strategy Chart", fontsize=14, fontweight="bold")
                ax.set_xlabel("Date", fontsize=11)
                ax.set_ylabel("Price (USD)", fontsize=11)
                ax.legend(loc="best", fontsize=9)
                ax.grid(alpha=0.3, linestyle=":")
                fig.autofmt_xdate()
                st.pyplot(fig)

            # 📊 Performance Tab
            with perf_tab:
                total_ret, bh_ret, win_rate, n_trades = calculate_metrics(df, price_col)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("📈 Strategy Return", f"{total_ret*100:.2f}%")
                with col_b:
                    st.metric("💼 Buy & Hold Return", f"{bh_ret*100:.2f}%")
                with col_c:
                    st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
                with col_d:
                    st.metric("🔄 Trades Executed", n_trades)

                # Equity curve comparison
                st.subheader("Equity Curve Comparison")
                fig2, ax2 = plt.subplots(figsize=(12, 4))
                ax2.plot(df["date"], df["equity_curve"], label="Strategy", linewidth=1.5, color="#06A77D")
                ax2.plot(df["date"], df["bh_equity"], label="Buy & Hold", linewidth=1.5, linestyle="--", color="#D62246")
                ax2.set_title("Strategy vs Buy & Hold", fontsize=12, fontweight="bold")
                ax2.set_xlabel("Date", fontsize=10)
                ax2.set_ylabel("Equity Multiplier", fontsize=10)
                ax2.legend(loc="best")
                ax2.grid(alpha=0.3, linestyle=":")
                fig2.autofmt_xdate()
                st.pyplot(fig2)

            # 📐 Indicators Tab
            with indicator_tab:
                last = df.iloc[-1]

                st.subheader("📐 Latest Indicator Snapshot")
                
                # Display RSI and MACD only if they were computed
                if use_rsi_macd:
                    st.write(
                        f"**RSI ({rsi_window}):** {last['rsi']:.1f} | "
                        f"**MACD:** {last['macd']:.4f} | **Signal:** {last['macd_signal']:.4f}"
                    )
                else:
                    st.info("RSI and MACD indicators are disabled. Enable 'Require RSI + MACD confirmation' to see them.")

                # Display volatility if enabled
                if use_vol_filter and max_vol_pct is not None:
                    vol = last.get("volatility", None)

                    if vol is not None and pd.notna(vol):
                        st.write(
                            f"**Rolling volatility ({vol_window}d):** "
                            f"{vol*100:.2f}% (max allowed {max_vol_pct:.1f}%)"
                        )
                    else:
                        st.write(
                            f"**Rolling volatility ({vol_window}d):** "
                            f"N/A (not enough data yet for the {vol_window}-day window)"
                        )
                else:
                    st.info("Volatility filter is disabled.")

                # Current position
                st.write(f"**Current Position:** {'LONG' if last['position'] == 1 else 'FLAT'}")
                st.write(f"**Latest Signal:** {last['signal_display']}")

            # 📅 Signals Tab
            with signals_tab:
                st.subheader("Recent Trading Signals")
                signal_df = df[["date_display", price_col, "signal_display", "position"]].tail(20).reset_index(drop=True)
                signal_df.columns = ["Date", "Price (USD)", "Signal", "Position"]
                st.dataframe(signal_df, width=800)

        st.markdown("---")

        # -------------------------------------------------
        # PORTFOLIO AGGREGATION (EQUAL WEIGHTED)
        # -------------------------------------------------
        if len(results) > 1:
            st.header("📦 Portfolio Analysis")
            st.write(f"**Equal-weighted portfolio** of {len(results)} tickers with ${portfolio_capital:,.0f} total capital")
            
            # Calculate portfolio metrics
            frames = []
            for t, (df, _) in results.items():
                tmp = df[["date", "equity_curve", "bh_equity"]].copy()
                tmp[f"{t}_equity"] = (portfolio_capital / len(results)) * tmp["equity_curve"]
                tmp[f"{t}_bh_equity"] = (portfolio_capital / len(results)) * tmp["bh_equity"]
                frames.append(tmp[["date", f"{t}_equity", f"{t}_bh_equity"]])

            portfolio_df = reduce(
                lambda left, right: pd.merge(left, right, on="date", how="outer"),
                frames
            ).sort_values("date")

            equity_cols = [c for c in portfolio_df.columns if c.endswith("_equity") and not "bh" in c]
            bh_cols = [c for c in portfolio_df.columns if c.endswith("_bh_equity")]
            
            portfolio_df[equity_cols] = portfolio_df[equity_cols].ffill()
            portfolio_df[bh_cols] = portfolio_df[bh_cols].ffill()
            
            portfolio_df["total_equity"] = portfolio_df[equity_cols].sum(axis=1)
            portfolio_df["total_bh_equity"] = portfolio_df[bh_cols].sum(axis=1)

            # Portfolio metrics
            portfolio_return = (portfolio_df["total_equity"].iloc[-1] / portfolio_capital - 1) * 100
            portfolio_bh_return = (portfolio_df["total_bh_equity"].iloc[-1] / portfolio_capital - 1) * 100
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric("📊 Portfolio Return", f"{portfolio_return:.2f}%")
            with col_p2:
                st.metric("💼 Portfolio B&H Return", f"{portfolio_bh_return:.2f}%")
            with col_p3:
                outperformance = portfolio_return - portfolio_bh_return
                st.metric("🎯 Outperformance", f"{outperformance:.2f}%", 
                         delta=f"{outperformance:.2f}%")

            # Portfolio equity curve
            st.subheader("Portfolio Equity Curves")
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(portfolio_df["date"], portfolio_df["total_equity"], 
                   linewidth=2, label="Strategy Portfolio", color="#06A77D")
            ax.plot(portfolio_df["date"], portfolio_df["total_bh_equity"], 
                   linewidth=2, linestyle="--", label="Buy & Hold Portfolio", color="#D62246")
            
            # Add individual ticker equity curves (lighter)
            for col in equity_cols:
                ticker_name = col.replace("_equity", "")
                ax.plot(portfolio_df["date"], portfolio_df[col], 
                       linewidth=0.8, alpha=0.4, linestyle=":")
            
            ax.set_title("Portfolio Performance Comparison", fontsize=14, fontweight="bold")
            ax.set_xlabel("Date", fontsize=11)
            ax.set_ylabel("Portfolio Value (USD)", fontsize=11)
            ax.legend(loc="best")
            ax.grid(alpha=0.3, linestyle=":")
            fig.autofmt_xdate()
            st.pyplot(fig)

            # Individual ticker contributions
            with st.expander("📊 Individual Ticker Contributions"):
                contrib_data = []
                for t, (df, price_col) in results.items():
                    ticker_return = (df["equity_curve"].iloc[-1] - 1) * 100
                    ticker_bh_return = (df["bh_equity"].iloc[-1] - 1) * 100
                    contrib_data.append({
                        "Ticker": t,
                        "Strategy Return": f"{ticker_return:.2f}%",
                        "B&H Return": f"{ticker_bh_return:.2f}%",
                        "Outperformance": f"{ticker_return - ticker_bh_return:.2f}%",
                        "Allocation": f"${portfolio_capital / len(results):,.0f}"
                    })
                
                contrib_df = pd.DataFrame(contrib_data)
                st.dataframe(contrib_df, width=800)

