from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime

class SymbolDetails(BaseModel):
    symbol: str
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    faName: str
    faBaseAsset: str
    faQuoteAsset: str
    stepSize: float
    tickSize: float
    minQty: float
    minNotional: float
    stats: dict  # Define more specific fields if available
    createdAt: datetime

class WallexSpotOrderResponseResult(BaseModel):
    symbol: str
    type: str  # 'LIMIT' | 'MARKET'
    side: str  # 'BUY' | 'SELL'
    price: str
    origQty: str
    sum: str
    executedPrice: str
    executedQty: str
    executedSum: str
    executedPercent: float
    status: str  # 'NEW' | 'FILLED' | 'CANCELED'
    active: bool
    clientOrderId: str
    transactTime: datetime
    quantity: Optional[List[str]]
    error_code: Optional[List[int]]

class WallexSpotOrderResponse(BaseModel):
    success: bool
    message: str
    result: WallexSpotOrderResponseResult

class WallexOTCPriceResponseResult(BaseModel):
    price: str
    price_expiresAt: datetime
    ttl: str
    current_time: datetime

class WallexOTCPriceResponse(BaseModel):
    success: bool
    message: str
    result: WallexOTCPriceResponseResult

class WallexAllMarketsResponse(BaseModel):
    success: bool
    message: str
    result: Dict[str, SymbolDetails]

class WallexOrderBlockResponse(BaseModel):
    price: str
    quantity: float
    sum: str

class WallexOrderBookResponseResult(BaseModel):
    ask: List[WallexOrderBlockResponse]
    bid: List[WallexOrderBlockResponse]

class WallexOrderBookResponse(BaseModel):
    success: bool
    message: str
    result: WallexOrderBookResponseResult

class WallexOrderBlockSocketResponse(BaseModel):
    price: str
    quantity: float
    sum: float

class WallexOrderBookSocketResponse(BaseModel):
    socket: Optional[str]
    channel: str
    data: Dict[str, WallexOrderBlockSocketResponse]

class WallexTradeSocketEvent(BaseModel):
    isBuyOrder: bool
    quantity: str
    price: str
    timestamp: datetime

class WallexMarketCapSocketEvent(BaseModel):
    symbol: str
    __24h_ch: float = Field(..., alias='24h_ch')
    __7d_ch: float = Field(..., alias='7d_ch')
    __24h_volume: str = Field(..., alias='24h_volume')
    __7d_volume: str = Field(..., alias='7d_volume')
    __24h_quoteVolume: str = Field(..., alias='24h_quoteVolume')
    __24h_highPrice: str = Field(..., alias='24h_highPrice')
    __24h_lowPrice: str = Field(..., alias='24h_lowPrice')
    lastPrice: str
    lastQty: str
    bidPrice: str
    askPrice: str
    lastTradeSide: str
    bidVolume: str
    askVolume: str
    bidCount: int
    askCount: int
    direction: Dict[str, float]
    createdAt: datetime

# Define additional models as needed for database interactions and other functionalities