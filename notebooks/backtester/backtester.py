# backtester.py

import pandas as pd

class Backtester:
    def __init__(self, initial_capital, leverage, transaction_cost, risk_per_trade):
        """
        Initialize Backtester with capital, leverage, transaction cost, and risk per trade.
        
        :param initial_capital: Starting capital.
        :param leverage: Leverage used for trades.
        :param transaction_cost: Transaction cost as a percentage.
        :param risk_per_trade: Risk per trade as a percentage of capital.
        """
        self.initial_capital = initial_capital
        self.leverage = leverage
        self.transaction_cost = transaction_cost
        self.risk_per_trade = risk_per_trade
        self.trades = []
        self.capital = initial_capital
        self.open_positions = []

    def run_backtest(self, data, strategy, timeframe, in_sample_split=0.7):
        """
        Run backtest using the given data and strategy.

        :param data: Dictionary containing price data for each symbol.
        :param strategy: Strategy object for entry/exit logic.
        :param timeframe: Timeframe key for selecting data (e.g., mt5.TIMEFRAME_H1).
        :param in_sample_split: Fraction of data to use for in-sample testing.
        :return: DataFrame of all trades.
        """
        for symbol, timeframes_data in data.items():
            # Select the timeframe's DataFrame
            symbol_data = timeframes_data[timeframe]

            # Split into in-sample and out-sample data
            in_sample_data = symbol_data.iloc[:int(len(symbol_data) * in_sample_split)]
            out_sample_data = symbol_data.iloc[int(len(symbol_data) * in_sample_split):]

            # Run the backtest for both in-sample and out-of-sample periods
            self._backtest_symbol(symbol, in_sample_data, strategy, 'In-sample')
            self._backtest_symbol(symbol, out_sample_data, strategy, 'Out-of-sample')

        return pd.DataFrame(self.trades)

    def _backtest_symbol(self, symbol, symbol_data, strategy, data_type):
        """
        Backtest a single symbol.

        :param symbol: The symbol being tested.
        :param symbol_data: DataFrame with historical price data.
        :param strategy: Strategy object for entry/exit logic.
        :param data_type: 'In-sample' or 'Out-of-sample'.
        """
        for i in range(len(symbol_data)):
            trade_signal = strategy.should_enter_trade(symbol_data, i)
            if trade_signal:
                # Pass data_type to _enter_position
                self._enter_position(symbol, trade_signal, symbol_data, i, data_type)
            
            self._exit_positions(symbol_data, i)

    def _enter_position(self, symbol, trade_signal, symbol_data, index, data_type):
        """
        Enter a new trade based on the trade signal.

        :param symbol: The symbol for the trade.
        :param trade_signal: 'long' or 'short' trade signal.
        :param symbol_data: DataFrame containing the symbol's price data.
        :param index: Current index in the DataFrame.
        :param data_type: Either 'In-sample' or 'Out-of-sample' indicating the data split.
        """
        entry_price = symbol_data['close'].iloc[index]
        stop_loss = entry_price * (1 - 0.02) if trade_signal == 'long' else entry_price * (1 + 0.02)
        take_profit = entry_price * (1 + 0.04) if trade_signal == 'long' else entry_price * (1 - 0.04)

        allocated_capital = self.capital * self.risk_per_trade / abs(entry_price - stop_loss)
        transaction_cost = allocated_capital * self.transaction_cost

        position = {
            'symbol': symbol,
            'entry_time': symbol_data.index[index],
            'entry_price': entry_price,
            'sl': stop_loss,
            'tp': take_profit,
            'position': trade_signal,
            'allocated_capital': allocated_capital,
            'transaction_cost': transaction_cost,
            'data_type': data_type  # Fix: Include data_type
        }

        self.open_positions.append(position)
        self.capital -= allocated_capital

    def _exit_positions(self, symbol_data, index):
        """
        Check exit conditions and close positions if needed.

        :param symbol_data: DataFrame containing the symbol's price data.
        :param index: Current index in the DataFrame.
        """
        for pos in self.open_positions.copy():
            if (pos['position'] == 'long' and symbol_data['close'].iloc[index] >= pos['tp']) or \
               (pos['position'] == 'short' and symbol_data['close'].iloc[index] <= pos['tp']):
                self._close_position(pos, symbol_data['close'].iloc[index], symbol_data.index[index])
            elif (pos['position'] == 'long' and symbol_data['close'].iloc[index] <= pos['sl']) or \
                 (pos['position'] == 'short' and symbol_data['close'].iloc[index] >= pos['sl']):
                self._close_position(pos, symbol_data['close'].iloc[index], symbol_data.index[index])

    def _close_position(self, position, close_price, exit_time):
        """
        Close the given position and log the trade.

        :param position: The position dictionary.
        :param close_price: The price at which the position is closed.
        :param exit_time: The time the position is closed.
        """
        pnl = (close_price - position['entry_price']) * self.leverage if position['position'] == 'long' else \
              (position['entry_price'] - close_price) * self.leverage

        self.trades.append({
            'symbol': position['symbol'],
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'entry_price': position['entry_price'],
            'close_price': close_price,
            'pnl': pnl - position['transaction_cost'],
            'capital': self.capital,
            'data_type': position['data_type']  # Include data_type in trade log
        })
        self.open_positions.remove(position)
        self.capital += pnl
