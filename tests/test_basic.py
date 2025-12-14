# tests/test_basic.py
"""
Basic tests for the auto-trading application.
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

# Import modules to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import compute_performance_stats
from src.strategy import calculate_sma

class TestMetrics(unittest.TestCase):
    """Test performance metrics calculations."""
    
    def setUp(self):
        """Set up test data."""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        self.df = pd.DataFrame({
            'date': dates,
            'equity_curve': np.linspace(1.0, 1.2, 100),  # 20% growth
            'strategy_returns_net': np.random.normal(0.001, 0.02, 100),
            'position': np.random.choice([0, 1], 100)
        })
    
    def test_compute_performance_stats(self):
        """Test performance statistics calculation."""
        stats = compute_performance_stats(self.df, 'close')
        
        # Check that all expected metrics are present
        expected_keys = ['total_return', 'CAGR', 'Sharpe', 'MaxDD', 'WinRate', 'ProfitFactor', 'Trades']
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Check reasonable ranges
        self.assertIsInstance(stats['total_return'], (int, float))
        self.assertIsInstance(stats['WinRate'], (int, float))
        self.assertTrue(0 <= stats['WinRate'] <= 1)

class TestStrategy(unittest.TestCase):
    """Test trading strategy functions."""
    
    def setUp(self):
        """Set up test price data."""
        self.df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 104, 103, 102, 101]
        })
    
    def test_calculate_sma(self):
        """Test SMA calculation."""
        result = calculate_sma(self.df, 'close', 3)
        
        # Check that SMA is calculated correctly
        self.assertIn('sma_3', result.columns)
        
        # First two values should be NaN (not enough data)
        self.assertTrue(pd.isna(result['sma_3'].iloc[0]))
        self.assertTrue(pd.isna(result['sma_3'].iloc[1]))
        
        # Third value should be average of first 3
        expected_sma_3 = (100 + 101 + 102) / 3
        self.assertAlmostEqual(result['sma_3'].iloc[2], expected_sma_3)

if __name__ == '__main__':
    unittest.main()