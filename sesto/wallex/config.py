import os
from dotenv import load_dotenv
from pydantic import BaseSettings, AnyUrl
from typing import Dict

load_dotenv()  # Load environment variables from a .env file

class WallexConfig(BaseSettings):
    Pairs: Dict[str, Dict]
    Fee: Dict[str, float]
    CapitalUSDT: float
    acceptableMargin: float
    URLs: Dict[str, AnyUrl]
    WALLEX_API_KEY: str

    class Config:
        env_file = ".env"

wallex_config = WallexConfig(
    Pairs={
        "BTC": {
            "QuantityPrecision": 6,
            "PricePrecision": {
                "USDT": 2,
                "TMN": 0
            },
            "MinimumQuantity": 1,
            "isActive": True
        },
        "ETH": {
            "QuantityPrecision": 5,
            "PricePrecision": {
                "USDT": 2,
                "TMN": 0
            },
            "MinimumQuantity": 1,
            "isActive": True
        },
        # Add other pairs similarly...
        "USDT": {
            "QuantityPrecision": 1,
            "PricePrecision": {
                "USDT": 5,
                "TMN": 0
            },
            "MinimumQuantity": 0.1,
            "isActive": True
        }
    },
    Fee={
        "USDT": 0.0025,
        "TMN": 0.0035,
        "OTC": 0.0035
    },
    CapitalUSDT=8,
    acceptableMargin=0.05,
    URLs={
        "MarketsEndpoint": "https://api.wallex.ir/v1/markets",
        "StatsEndpoint": "https://api.wallex.ir/v1/currencies/stats",
        "OrderBookEndpoint": "https://api.wallex.ir/v1/depth",
        "TradesEndpoint": "https://api.wallex.ir/v1/trades",
        "CandlesEndpoint": "https://api.wallex.ir/v1/udf/history",
        "ProfileEndpoint": "https://api.wallex.ir/v1/account/profile",
        "ProfileFeeEndpoint": "https://api.wallex.ir/v1/account/fee",
        "ProfileAuthEndpoint": "https://api.wallex.ir/v1/account/oauth",
        "ProfileBalancesEndpoint": "https://api.wallex.ir/v1/account/balances",
        "RialWithdrawalEndpoint": "https://api.wallex.ir/v1/account/money-withdrawal",
        "CryptoDepositsEndpoint": "https://api.wallex.ir/v1/account/crypto-deposit",
        "CryptoWithdrawalsEndpoint": "https://api.wallex.ir/v1/account/crypto-withdrawal",
        "PostCryptoWithdrawalEndpoint": "https://api.wallex.ir/v1/account/crypto-withdrawal",
        "PostSpotOrderEndpoint": "https://api.wallex.ir/v1/account/orders",
        "OrderDataEndpoint": "https://api.wallex.ir/v1/account/orders",
        "CancelSpotOrderEndpoint": "https://api.wallex.ir/v1/account/orders",
        "GetMyOpenOrdersEndpoint": "https://api.wallex.ir/v1/account/openOrders",
        "GetMyOpenTradesEndpoint": "https://api.wallex.ir/v1/account/trades",
        "OTCMarketsEndpoint": "https://api.wallex.ir/v1/otc/markets",
        "OTCPriceEndpoint": "https://api.wallex.ir/v1/otc/price",
        "PostOTCOrderEndpoint": "https://api.wallex.ir/v1/account/otc/orders",
        "SocketEndpoint": "https://api.wallex.ir"
    },
    WALLEX_API_KEY=os.getenv("WALLEX_API_KEY")
)

WallexConfig = wallex_config