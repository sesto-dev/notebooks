# data_handler.py
import MetaTrader5 as mt5
import pandas as pd

class DataHandler:
    def __init__(self, symbols, timeframe, bars):
        self.symbols = symbols
        self.timeframe = timeframe
        self.bars = bars
    
    def fetch_data(self):
        if not mt5.initialize():
            raise RuntimeError("Failed to initialize MT5")

        data = {}
        for symbol in self.symbols:
            rates = mt5.copy_rates_from_pos(symbol, self.timeframe, 0, self.bars)
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            data[symbol] = df
        
        mt5.shutdown()
        return data
