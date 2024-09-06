# test_backtester.py
import unittest
from data_handler import DataHandler
from backtester import Backtester
from strategy import Strategy

class TestBacktester(unittest.TestCase):
    def setUp(self):
        # Setup initial configurations for the tests
        self.symbols = ['EURUSD']
        self.timeframe = [mt5.TIMEFRAME_H1]
        self.bars = 1000
        self.initial_capital = 10000
        self.leverage = 10
        self.transaction_cost = 0.001
        self.risk_per_trade = 0.01

        # Mock strategy for testing
        class MockStrategy(Strategy):
            def should_enter_trade(self, symbol_data, index):
                return 'long' if index % 2 == 0 else 'short'

            def should_exit_trade(self, open_position, symbol_data, index):
                return True if index % 2 == 1 else False

        self.strategy = MockStrategy()

        # Mock data handler
        self.data_handler = DataHandler(self.symbols, self.timeframe, self.bars)
        self.data = self.data_handler.fetch_data()

    def test_backtest_with_mock_strategy(self):
        backtester = Backtester(
            initial_capital=self.initial_capital,
            leverage=self.leverage,
            transaction_cost=self.transaction_cost,
            risk_per_trade=self.risk_per_trade
        )
        trades_df = backtester.run_backtest(self.data, self.strategy)
        
        # Test if trades DataFrame is populated
        self.assertGreater(len(trades_df), 0)

    def test_calculate_metrics(self):
        backtester = Backtester(
            initial_capital=self.initial_capital,
            leverage=self.leverage,
            transaction_cost=self.transaction_cost,
            risk_per_trade=self.risk_per_trade
        )
        trades_df = backtester.run_backtest(self.data, self.strategy)
        
        # Test if metrics are correctly calculated
        self.assertGreater(trades_df['pnl'].sum(), 0)

if __name__ == '__main__':
    unittest.main()
