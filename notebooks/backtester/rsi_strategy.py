# rsi_strategy.py
import ta
from strategy import Strategy

class RSIStrategy(Strategy):
    def __init__(self, rsi_length, rsi_lower, rsi_upper):
        self.rsi_length = rsi_length
        self.rsi_lower = rsi_lower
        self.rsi_upper = rsi_upper
    
    def should_enter_trade(self, symbol_data, index):
        rsi = ta.rsi(symbol_data['close'], self.rsi_length).iloc[index]
        if rsi < self.rsi_lower:
            return 'long'
        elif rsi > self.rsi_upper:
            return 'short'
        return None
    
    def should_exit_trade(self, open_position, symbol_data, index):
        rsi = ta.rsi(symbol_data['close'], self.rsi_length).iloc[index]
        if (open_position['position'] == 'long' and rsi > self.rsi_upper) or \
           (open_position['position'] == 'short' and rsi < self.rsi_lower):
            return True
        return False
