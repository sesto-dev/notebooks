from typing import Dict
from .types import WallexMarketCapSocketEvent, WallexOrderBookResponse
from threading import Lock

# Thread-safe dictionaries for temporary storage
WallexTempMarketData: Dict[str, WallexMarketCapSocketEvent] = {}
WallexTempOTCMarketData: Dict[str, Dict[str, float]] = {}
WallexTempOrderBookData: Dict[str, WallexOrderBookResponse] = {}

# Locks for thread-safe operations
market_data_lock = Lock()
otc_market_data_lock = Lock()
order_book_data_lock = Lock()