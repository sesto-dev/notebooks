import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict
from constants import MT5Timeframe

from api.fetch import _make_request

def symbol_info_tick(symbol):
    """
    Fetch symbol tick information.

    Args:
        symbol (str): The symbol to fetch tick information for.
    """
    endpoint = f'/symbol_info_tick/{symbol}'
    return _make_request('GET', endpoint)

def symbol_info(symbol):
    """
    Fetch symbol information.

    Args:
        symbol (str): The symbol to fetch information for.
    """
    endpoint = f'/symbol_info/{symbol}'
    return _make_request('GET', endpoint)


def fetch_data_pos(symbol: str, timeframe: MT5Timeframe, bars: int) -> pd.DataFrame:
    try:
        endpoint = '/fetch_data_pos'
        params = {
            'symbol': symbol,
            'timeframe': timeframe,
            'bars': bars
        }
        rates = _make_request('POST', endpoint, params=params)
        if rates is None:
            print(f"Failed to fetch data for symbol: {symbol} on timeframe: {timeframe}")
            return pd.DataFrame()
        df = pd.DataFrame(rates)
        df.dropna(subset='time', inplace=True)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.reset_index(drop=True, inplace=True)
        
        return df
    except Exception as e:
        print(f"Exception fetching data for {symbol} on {timeframe}: {e}")
        return pd.DataFrame()

def fetch_data_range(symbol: str, timeframe: MT5Timeframe, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    try:
        endpoint = '/copy_rates_range'
        params = {
            'symbol': symbol,
            'timeframe': timeframe,
            'from_date': from_date,
            'to_date': to_date
        }
        rates = _make_request('POST', endpoint, params=params)
        if rates is None:
            print(f"Failed to fetch data for symbol: {symbol} on timeframe: {timeframe}")
            return pd.DataFrame()
        df = pd.DataFrame(rates)
        df.dropna(subset='time', inplace=True)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.reset_index(drop=True, inplace=True)

        return df
    except Exception as e:
        print(f"Exception fetching data for {symbol} on {timeframe}: {e}")
        return pd.DataFrame()