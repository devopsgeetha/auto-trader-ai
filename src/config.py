# config.py
"""
Configuration settings for the auto-trading application.
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradingConfig:
    """Configuration for trading parameters."""
    default_capital: float = 10_000
    max_position_size: float = 0.1  # 10% of portfolio
    default_stop_loss: float = 0.05  # 5%
    default_take_profit: float = 0.10  # 10%
    trade_cost_bps: int = 10  # 10 basis points per trade

@dataclass 
class APIConfig:
    """Configuration for API keys and endpoints."""
    pass  # No external API keys required (uses yfinance)

@dataclass
class ModelConfig:
    """Configuration for AI models."""
    transformer_seq_len: int = 30
    transformer_d_model: int = 32
    transformer_nhead: int = 2
    transformer_layers: int = 2
    training_epochs: int = 40
    learning_rate: float = 0.005

# Global configuration instances
trading_config = TradingConfig()
api_config = APIConfig()
model_config = ModelConfig()