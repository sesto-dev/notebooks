from enum import Enum
import MetaTrader5 as mt5
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field

class MT5Timeframe(Enum):
    M1 = mt5.TIMEFRAME_M1       # 1-minute
    M5 = mt5.TIMEFRAME_M5       # 5-minute
    M15 = mt5.TIMEFRAME_M15     # 15-minute
    M30 = mt5.TIMEFRAME_M30     # 30-minute
    H1 = mt5.TIMEFRAME_H1       # 1-hour
    H4 = mt5.TIMEFRAME_H4       # 4-hour
    D1 = mt5.TIMEFRAME_D1       # daily
    W1 = mt5.TIMEFRAME_W1       # weekly
    MN1 = mt5.TIMEFRAME_MN1     # monthly

CURRENCY_PAIRS: List[str] = ['USDJPY','USDCHF','USDCAD','EURUSD','EURGBP','EURJPY','EURCHF','EURCAD','EURAUD','EURNZD','GBPUSD','GBPJPY','GBPCHF','GBPCAD','GBPAUD','GBPNZD','CHFJPY','CADJPY','CADCHF','AUDUSD','AUDJPY','AUDCHF','AUDCAD','AUDNZD','NZDUSD','NZDJPY','NZDCHF','NZDCAD']
CURRENCIES: List[str] = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]