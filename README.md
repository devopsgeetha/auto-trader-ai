# Auto-Trading AI

A paper trading application built with Streamlit that implements various trading strategies with AI-powered predictions.

## Features

- 📈 Multiple technical indicators (SMA, RSI, MACD)
- 🤖 AI-powered direction prediction using transformer models
- 📊 Real-time portfolio tracking and performance metrics
- 🎯 Custom ticker input - analyze any stock symbol
- 📦 Enhanced portfolio view with individual ticker contributions
- 📋 Comprehensive backtesting with Buy & Hold comparison
- 💼 Paper trading simulation (no real money involved)
- 🎨 Professional charts with BUY/SELL signal markers

## Setup

Choose either **Docker** (recommended) or **Local** setup:

### Option 1: Docker Deployment (Recommended) 🐳

#### Prerequisites
- Docker and Docker Compose installed

#### Quick Start
```bash
# 1. Clone the repository
git clone <repository-url>
cd auto-trader-ai

# 2. Build and run with Docker Compose
docker-compose up -d

# 5. Access the app
# Open browser: http://localhost:8501
```

#### Docker Commands
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Stop and remove volumes
docker-compose down -v
```

### Option 2: Local Setup

#### 1. Clone the repository
```bash
git clone <repository-url>
cd auto-trader-ai
```

#### 2. Create virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the application
```bash
streamlit run trader_app.py
```

The app will be available at http://localhost:8501

## Project Structure

```
auto-trader-ai/
├── trader_app.py          # Main Streamlit application
├── data_provider.py       # Yahoo Finance data fetching
├── strategy.py           # Trading strategy implementations
├── ai_models.py          # AI prediction models
├── model_transformer.py  # Transformer-based price prediction
# live trading interface removed
├── metrics.py           # Performance calculation utilities
└── requirements.txt     # Python dependencies
```

## Usage

1. **Select Tickers**: Choose from preset tickers or enter custom symbols (e.g., META, NFLX)
2. **Configure Strategy**: Adjust SMA windows, RSI/MACD settings, risk management
3. **Enable AI** (optional): Toggle transformer-based predictions
4. **Set Portfolio**: Define capital and trading costs
5. **Run Strategy**: Execute backtesting and view results in 4 tabs:
   - 📈 Chart with price, SMAs, and signal markers
   - 📊 Performance metrics and equity curves
   - 📐 Technical indicators (RSI, MACD, volatility)
   - 📅 Recent trading signals
6. **Portfolio View**: Automatically shown when analyzing 2+ tickers

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