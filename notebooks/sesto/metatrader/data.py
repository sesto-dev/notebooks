import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

if not mt5.initialize():
    print(f"MetaTrader 5 initialization failed: {mt5.last_error()}")
else:
    print("MetaTrader 5 initialized successfully.")

data = {}

def fetch_data_pos(symbol: str, timeframe: int, bars: int) -> pd.DataFrame:
    try:
        # Fetch data using MetaTrader 5 API
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        
        if rates is None:
            print(f"Failed to fetch data for symbol: {symbol}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error
        
        # Convert the data into a DataFrame
        data = pd.DataFrame(rates)
        
        # Convert the time in seconds to datetime
        data['time'] = pd.to_datetime(data['time'], unit='s')

        return data

    except Exception as e:
        print(f"An exception occurred while fetching data for symbol {symbol}: {e}")
        return pd.DataFrame() 
    
def fetch_data_range(symbol: str, timeframe: int, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    try:
        # Fetch data using MetaTrader 5 API
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        
        if rates is None:
            print(f"Failed to fetch data for symbol: {symbol}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error
        
        # Convert the data into a DataFrame
        data = pd.DataFrame(rates)
        
        # Convert the time in seconds to datetime
        data['time'] = pd.to_datetime(data['time'], unit='s')

        return data

    except Exception as e:
        print(f"An exception occurred while fetching data for symbol {symbol}: {e}")
        return pd.DataFrame() 


def fill_data_pos(pairs, timeframe, bars):
    for pair in pairs:
        symbol_data = fetch_data_pos(pair, timeframe, bars)
        if symbol_data.empty:
            print(f"No data fetched for pair: {pair}")
        else:
            print(f"Fetched data for pair: {pair}")
        data[pair] = symbol_data

def fill_data_range(pairs, timeframe, from_date: datetime, to_date: datetime):
    for pair in pairs:
        symbol_data = fetch_data_range(pair, timeframe, from_date, to_date) 

        if symbol_data.empty:
            print(f"No data fetched for pair: {pair}")
        else:
            print(f"Fetched data for pair: {pair}")
        data[pair] = symbol_data
