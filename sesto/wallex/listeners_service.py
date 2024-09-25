import asyncio
import json
import websockets
from typing import Callable
from .config import WallexConfig
from .types import WallexTradeSocketEvent, WallexMarketCapSocketEvent
from .endpoints_service import WallexEndpointsService
from .lib import extract_wallex_crypto_symbol_from_symbol
from .temp import (
    WallexTempMarketData,
    WallexTempOrderBookData,
    market_data_lock,
    order_book_data_lock
)
from loguru import logger
from aiomysql import create_pool
from datetime import datetime

class WallexListenerService:
    def __init__(self, on_trade: Callable, on_market_cap: Callable, on_depth_update: Callable):
        self.websocket_url = WallexConfig.URLs.get("SocketEndpoint")
        self.on_trade = on_trade
        self.on_market_cap = on_market_cap
        self.on_depth_update = on_depth_update
        self.endpoints_service = WallexEndpointsService()
        self.websocket = None
        self.keep_listening = True

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.websocket_url, subprotocols=["protocolOne"])  # Adjust subprotocols if needed
            logger.info("Connected to Wallex WebSocket.")
            await self.subscribe_channels()
            await self.listen()
        except Exception as e:
            logger.error(f"Error initiating Wallex Socket - Wallex API: {e}")

    async def subscribe_channels(self):
        pairs = WallexConfig.Pairs.keys()
        for pair in pairs:
            config = WallexConfig.Pairs.get(pair)
            if config.get("isActive"):
                symbols = [f"{pair}USDT", f"{pair}TMN"]
                for symbol in symbols:
                    await self.websocket.send(json.dumps({"action": "subscribe", "channel": f"{symbol}@marketCap"}))
                    await self.websocket.send(json.dumps({"action": "subscribe", "channel": f"{symbol}@trade"}))
                    await self.websocket.send(json.dumps({"action": "subscribe", "channel": f"{symbol}@sellDepth"}))
                    await self.websocket.send(json.dumps({"action": "subscribe", "channel": f"{symbol}@buyDepth"}))
                    logger.info(f"Subscribed to channels for {symbol}")

    async def listen(self):
        async for message in self.websocket:
            try:
                data = json.loads(message)
                channel = data.get("channel")
                symbol = channel.split('@')[0]
                event_type = channel.split('@')[1]

                if event_type == "trade":
                    trade_event = WallexTradeSocketEvent(**data)
                    async with market_data_lock:
                        await self.on_trade(symbol, trade_event)
                elif event_type == "marketCap":
                    market_cap_event = WallexMarketCapSocketEvent(**data)
                    async with market_data_lock:
                        WallexTempMarketData[symbol] = market_cap_event
                        await self.on_market_cap(symbol, market_cap_event)
                elif event_type in ["sellDepth", "buyDepth"]:
                    # Handle depth updates
                    await self.on_depth_update(symbol, data)
                else:
                    logger.warning(f"Unhandled event type: {event_type} for symbol: {symbol}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def close(self):
        self.keep_listening = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Closed Wallex WebSocket connection.")
        await self.endpoints_service.close_session()