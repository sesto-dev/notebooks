from enum import Enum

class NobitexSymbol(Enum):
    BTC = "BTC"
    ETH = "ETH"
    BNB = "BNB"
    LTC = "LTC"
    MATIC = "MATIC"
    SOL = "SOL"
    ETC = "ETC"
    TRX = "TRX"
    SHIB = "SHIB"
    DOGE = "DOGE"
    XRP = "XRP"
    ADA = "ADA"
    FTM = "FTM"
    LINK = "LINK"
    UNI = "UNI"
    MKR = "MKR"
    SAND = "SAND"
    AAVE = "AAVE"
    DOT = "DOT"
    BCH = "BCH"
    MANA = "MANA"
    GMT = "GMT"
    EOS = "EOS"
    AXS = "AXS"
    USDT = "USDT"
    AVAX = "AVAX"
    PMN = "PMN"
    XLM = "XLM"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"

class OrderStatus(Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    CANCELED = "CANCELED"