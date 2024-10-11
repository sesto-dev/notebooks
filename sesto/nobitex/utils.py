from typing import Dict, List
from .models import NobitexSymbol

def transform_order_book(response: Dict) -> Dict[str, List[Dict]]:
    def transform_order_block(block: List[str]) -> Dict:
        return {
            "price": float(block[0]),
            "quantity": float(block[1]),
            "sum": None
        }

    return {
        "ask": [transform_order_block(block) for block in response['asks']],
        "bid": [transform_order_block(block) for block in response['bids']]
    }

def extract_crypto_symbol(symbol: str) -> NobitexSymbol:
    for nobitex_symbol in NobitexSymbol:
        if symbol.startswith(nobitex_symbol.value):
            return nobitex_symbol
    raise ValueError(f"Invalid symbol: {symbol}")

def get_best_order_blocks(order_book: Dict[str, List[Dict]]):
    ask_price = min(order_book['ask'], key=lambda x: x['price'])
    bid_price = max(order_book['bid'], key=lambda x: x['price'])
    return {"ask_price": ask_price, "bid_price": bid_price}

def calculate_nobitex_commission(position_size_usd: float) -> float:
    commission = position_size_usd * 0.00025
    return commission