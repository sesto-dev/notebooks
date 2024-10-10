import asyncio
from typing import Dict, Any, Callable
from .temp import WallexTempOrderBookData
from .types import WallexOrderBookResponse, WallexTempMarketData
from .config import WallexConfig

async def get_active_wallex_arbitrage_attempts_from_db(pool) -> list:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT * FROM arbitrage_attempt
                WHERE Exchange = 'WALLEX'
                AND isSubmitted = TRUE
                AND isCompleted = FALSE
                AND isCancelled = FALSE
            """)
            results = await cur.fetchall()
            # Convert to list of dicts or your ORM models
            return results

def convert_socket_response_to_order_book_data(socket_response: Dict[str, Any]) -> list:
    order_book_data = []
    for key, value in socket_response.items():
        if key not in ["socket", "channel"]:
            order_block = {
                "price": float(value["price"]),
                "quantity": float(value["quantity"]),
                "sum": float(value["sum"])
            }
            order_book_data.append(order_block)
    return order_book_data

def is_temp_market_data_valid(symbol: str) -> bool:
    event = WallexTempMarketData.get(symbol)
    if not event:
        return False
    # Add validation logic as needed
    return True

def is_temp_order_book_data_valid(symbol: str) -> bool:
    order_book = WallexTempOrderBookData.get(symbol)
    if not order_book:
        return False
    # Add validation logic as needed
    return True

def delay(seconds: float):
    return asyncio.sleep(seconds)

async def process_with_delay(items: list, delay_ms: int, callback: Callable):
    for item in items:
        callback(item)
        await asyncio.sleep(delay_ms / 1000.0)

# Add more utility functions as needed