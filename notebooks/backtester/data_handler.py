# data_handler.py
import MetaTrader5 as mt5
import pandas as pd

class DataHandler:
    def __init__(self, symbols, timeframes, bars):
        """
        Initialize DataHandler with symbols, timeframes, and bars.
        
        :param symbols: List of symbols (e.g., ['EURUSD', 'GBPUSD']).
        :param timeframes: List of timeframes (e.g., [mt5.TIMEFRAME_H1, mt5.TIMEFRAME_D1]).
        :param bars: Number of bars to fetch for each symbol.
        """
        self.symbols = symbols
        self.timeframes = timeframes
        self.bars = bars
    
    def fetch_data(self):
        """
        Fetch data for each symbol and each timeframe.
        
        :return: Dictionary with symbols as keys and a dictionary of DataFrames (one per timeframe).
        """
        if not mt5.initialize():
            raise RuntimeError("Failed to initialize MT5")

        data = {}
        for symbol in self.symbols:
            symbol_data = {}
            for timeframe in self.timeframes:
                rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, self.bars)
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.set_index('time', inplace=False)
                symbol_data[timeframe] = df
            data[symbol] = symbol_data
        
        mt5.shutdown()
        return data
