import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .types import (
    WallexAllMarketsResponse,
    WallexOrderBookResponse,
    WallexTradeSocketEvent,
    WallexMarketCapSocketEvent,
    WallexSpotOrderResponse,
    WallexOTCPriceResponse
)
from .config import WallexConfig
from .lib import extract_wallex_crypto_symbol_from_symbol
from .temp import WallexTempOrderBookData
from loguru import logger

class WallexEndpointsService:
    def __init__(self):
        self.headers = {
            'X-API-Key': WallexConfig.WALLEX_API_KEY,
            'Content-Type': 'application/json'
        }
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        await self.session.close()

    async def get_all_markets(self) -> Optional[WallexAllMarketsResponse]:
        url = WallexConfig.URLs.get("MarketsEndpoint")
        try:
            async with self.session.get(url) as response:
                data = await response.json()
                return WallexAllMarketsResponse(**data)
        except Exception as e:
            logger.error(f"Error while getting all markets - Wallex API Endpoints Service: {e}")
            return None

    async def get_stats(self) -> Optional[Dict[str, Any]]:
        url = WallexConfig.URLs.get("StatsEndpoint")
        try:
            async with self.session.get(url) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while getting stats - Wallex API Endpoints Service: {e}")
            return None

    async def get_order_book(self, symbol: str) -> Optional[WallexOrderBookResponse]:
        url = WallexConfig.URLs.get("OrderBookEndpoint")
        params = {'symbol': symbol}
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return WallexOrderBookResponse(**data)
        except Exception as e:
            logger.error(f"Error while getting order book for {symbol} - Wallex API Endpoints Service: {e}")
            return None

    async def get_trades(self, symbol: str) -> Optional[Dict[str, Any]]:
        url = WallexConfig.URLs.get("TradesEndpoint")
        params = {'symbol': symbol}
        try:
            async with self.session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while getting trades for {symbol} - Wallex API Endpoints Service: {e}")
            return None

    async def post_spot_order(self, params: Dict[str, Any]) -> Optional[WallexSpotOrderResponse]:
        url = WallexConfig.URLs.get("PostSpotOrderEndpoint")
        try:
            async with self.session.post(url, json=params) as response:
                data = await response.json()
                return WallexSpotOrderResponse(**data)
        except Exception as e:
            logger.error(f"Error while posting spot order - Wallex API Endpoints Service: {e}")
            return None

    async def get_order_data(self, client_order_id: str) -> Optional[WallexSpotOrderResponse]:
        url = f"{WallexConfig.URLs.get('OrderDataEndpoint')}/{client_order_id}"
        try:
            async with self.session.get(url) as response:
                data = await response.json()
                return WallexSpotOrderResponse(**data)
        except Exception as e:
            logger.error(f"Error while getting order data for {client_order_id} - Wallex API Endpoints Service: {e}")
            return None

    async def cancel_spot_order(self, client_order_id: str) -> Optional[Dict[str, Any]]:
        url = f"{WallexConfig.URLs.get('CancelSpotOrderEndpoint')}/{client_order_id}"
        try:
            async with self.session.delete(url) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while canceling order {client_order_id} - Wallex API Endpoints Service: {e}")
            return None

    async def get_my_open_orders(self, symbol: Optional[str] = None) -> Optional[Dict[str, Any]]:
        url = WallexConfig.URLs.get("GetMyOpenOrdersEndpoint")
        params = {}
        if symbol:
            params['symbol'] = symbol
        try:
            async with self.session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while getting my open orders - Wallex API Endpoints Service: {e}")
            return None

    async def get_my_open_trades(self, symbol: Optional[str] = None) -> Optional[Dict[str, Any]]:
        url = WallexConfig.URLs.get("GetMyOpenTradesEndpoint")
        params = {}
        if symbol:
            params['symbol'] = symbol
        try:
            async with self.session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while getting my open trades - Wallex API Endpoints Service: {e}")
            return None

    async def get_otc_markets(self) -> Optional[Dict[str, Any]]:
        url = WallexConfig.URLs.get("OTCMarketsEndpoint")
        try:
            async with self.session.get(url) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while getting OTC markets - Wallex API Endpoints Service: {e}")
            return None

    async def get_otc_price(self, symbol: str, side: str) -> Optional[WallexOTCPriceResponse]:
        url = WallexConfig.URLs.get("OTCPriceEndpoint")
        params = {'symbol': symbol, 'side': side}
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return WallexOTCPriceResponse(**data)
        except Exception as e:
            logger.error(f"Error while getting OTC price for {symbol} - Wallex API Endpoints Service: {e}")
            return None

    async def post_otc_order(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = WallexConfig.URLs.get("PostOTCOrderEndpoint")
        try:
            async with self.session.post(url, json=params) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error while posting OTC order - Wallex API Endpoints Service: {e}")
            return None

    # Add other endpoint methods as needed