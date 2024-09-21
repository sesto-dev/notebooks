import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
from typing import List, Dict
from sesto.constants import MT5Timeframe

if not mt5.initialize():
    print(f"MetaTrader 5 initialization failed: {mt5.last_error()}")
else:
    print("MetaTrader 5 initialized successfully.")

# Nested dictionary to store data: {timeframe: {symbol: DataFrame}}
data = {tf: {} for tf in MT5Timeframe}

def fetch_data_pos(symbol: str, timeframe: MT5Timeframe, bars: int) -> pd.DataFrame:
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe.value, 0, bars)
        if rates is None:
            print(f"Failed to fetch data for symbol: {symbol} on timeframe: {timeframe}")
            return pd.DataFrame()
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    except Exception as e:
        print(f"Exception fetching data for {symbol} on {timeframe}: {e}")
        return pd.DataFrame()

def fetch_data_range(symbol: str, timeframe: MT5Timeframe, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    try:
        rates = mt5.copy_rates_range(symbol, timeframe.value, from_date, to_date)
        if rates is None:
            print(f"Failed to fetch data for symbol: {symbol} on timeframe: {timeframe}")
            return pd.DataFrame()
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    except Exception as e:
        print(f"Exception fetching data for {symbol} on {timeframe}: {e}")
        return pd.DataFrame()

def fill_data_pos(pairs, timeframe: MT5Timeframe, bars):
    for pair in pairs:
        symbol_data = fetch_data_pos(pair, timeframe, bars)
        if symbol_data.empty:
            print(f"No data fetched for pair: {pair} on timeframe: {timeframe}")
        else:
            print(f"Fetched data for pair: {pair} on timeframe: {timeframe}")
        data[timeframe][pair] = symbol_data

def fill_data_range(pairs, timeframe: MT5Timeframe, from_date: datetime, to_date: datetime):
    for pair in pairs:
        symbol_data = fetch_data_range(pair, timeframe, from_date, to_date)
        if symbol_data.empty:
            print(f"No data fetched for pair: {pair} on timeframe: {timeframe}")
        else:
            print(f"Fetched data for pair: {pair} on timeframe: {timeframe}")
        data[timeframe][pair] = symbol_data

def fetch_data_all_timeframes(pairs: List[str], timeframes: List[MT5Timeframe], from_date: datetime, to_date: datetime):
    for timeframe in timeframes:
        fill_data_range(pairs, timeframe, from_date, to_date)