# backtester.py
import pandas as pd

class Backtester:
    def __init__(self, initial_capital, leverage, transaction_cost, capital_per_trade):
        self.initial_capital = initial_capital
        self.leverage = leverage
        self.transaction_cost = transaction_cost
        self.capital_per_trade = capital_per_trade
        self.trades = []
    
    def run_backtest(self, data, strategy):
        capital = self.initial_capital
        open_positions = []
        
        for symbol, symbol_data in data.items():
            for i in range(len(symbol_data)):
                trade_signal = strategy.should_enter_trade(symbol_data, i)
                if trade_signal and not open_positions:
                    # Execute trade logic
                    entry_price = symbol_data['close'].iloc[i]
                    trade_time = symbol_data['time'].iloc[i]
                    allocated_capital = capital * self.capital_per_trade
                    spread = entry_price * 0.03
                    tp = entry_price + spread if trade_signal == 'long' else entry_price - spread
                    sl = entry_price - (spread / 2) if trade_signal == 'long' else entry_price + (spread / 2)
                    transaction_cost = allocated_capital * self.transaction_cost

                    open_positions.append({
                        'symbol': symbol,
                        'position': trade_signal,
                        'entry_time': trade_time,
                        'entry_price': entry_price,
                        'sl': sl,
                        'tp': tp,
                        'allocated_capital': allocated_capital,
                        'transaction_cost': transaction_cost
                    })
                    capital -= allocated_capital
                
                # Handle exit logic
                for pos in open_positions.copy():
                    if strategy.should_exit_trade(pos, symbol_data, i):
                        exit_price = symbol_data['close'].iloc[i]
                        profit = (exit_price - pos['entry_price']) * self.leverage * pos['allocated_capital'] if pos['position'] == 'long' else \
                                 (pos['entry_price'] - exit_price) * self.leverage * pos['allocated_capital']
                        capital += profit - pos['transaction_cost']
                        max_drawdown = (pos['entry_price'] - symbol_data['close'].min()) * self.leverage * pos['allocated_capital'] if pos['position'] == 'long' else \
                                       (symbol_data['close'].max() - pos['entry_price']) * self.leverage * pos['allocated_capital']

                        self.trades.append({
                            'symbol': pos['symbol'],
                            'entry_time': pos['entry_time'],
                            'exit_time': trade_time,
                            'entry_price': pos['entry_price'],
                            'close_price': exit_price,
                            'pnl': profit - pos['transaction_cost'],
                            'max_drawdown': max_drawdown,
                            'tp': pos['tp'],
                            'sl': pos['sl'],
                            'position': pos['position'],
                            'capital': capital
                        })
                        open_positions.remove(pos)
        
        # Return trades as a DataFrame
        return pd.DataFrame(self.trades)
