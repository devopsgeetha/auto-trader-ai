# Auto-Trading AI

A paper trading application built with Streamlit that implements various trading strategies with AI-powered predictions.

## Features

- 📈 Multiple technical indicators (SMA, RSI, MACD)
- 🤖 AI-powered direction prediction using transformer models
- 📊 Real-time portfolio tracking and performance metrics
- 🔄 Live price updates with auto-refresh
- 📋 Comprehensive backtesting and analysis
- 💼 Paper trading simulation (no real money involved)

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd auto-trader-ai
```

### 2. Create virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file or set environment variables:

```bash
# Required for AlphaVantage data provider
ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key

# Optional: For live trading (Alpaca)
ALPACA_KEY=your_alpaca_api_key
ALPACA_SECRET=your_alpaca_secret_key
```

**Get API Keys:**
- AlphaVantage: https://www.alphavantage.co/support/#api-key
- Alpaca (paper trading): https://alpaca.markets/

### 5. Run the application
```bash
streamlit run trader_app.py
```

## Project Structure

```
auto-trader-ai/
├── trader_app.py          # Main Streamlit application
├── data_provider.py       # AlphaVantage data fetching
├── strategy.py           # Trading strategy implementations
├── ai_models.py          # AI prediction models
├── model_transformer.py  # Transformer-based price prediction
├── live_trading.py       # Live trading interface (Alpaca)
├── metrics.py           # Performance calculation utilities
└── requirements.txt     # Python dependencies
```

## Usage

1. **Select Tickers**: Choose from predefined tickers or add your own
2. **Configure Strategy**: Adjust SMA windows, RSI/MACD settings
3. **Enable AI**: Toggle transformer-based predictions
4. **Set Portfolio**: Define capital and trading costs
5. **Run Strategy**: Execute backtesting and view results

## Features Detail

### Technical Indicators
- **SMA Crossover**: Short/long moving average strategy
- **RSI**: Relative Strength Index for momentum
- **MACD**: Moving Average Convergence Divergence
- **Volatility Filter**: Risk management based on price volatility

### AI Prediction
- Transformer-based neural network for price direction
- Trains on historical returns data
- Provides probability scores for buy/sell signals

### Risk Management
- Stop-loss and take-profit levels
- Position sizing based on portfolio capital
- Transaction cost modeling

## Disclaimer

⚠️ **This is a paper trading application for educational purposes only.**

- No real money is involved
- Past performance does not guarantee future results
- Always do your own research before making investment decisions
- Consider consulting with financial professionals

## License

This project is for educational purposes. Please ensure compliance with financial regulations in your jurisdiction.