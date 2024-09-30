from typing import Dict, Any
from .models import NobitexSymbol

class NobitexConfig:
    BASE_URL = "https://api.nobitex.ir"
    
    PAIRS: Dict[NobitexSymbol, Dict[str, Any]] = {
        NobitexSymbol.BTC: {
            "quantity_precision": 6,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.ETH: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.BNB: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.LTC: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.MATIC: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 3, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.SOL: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.ETC: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.TRX: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.SHIB: {
            "quantity_precision": 0,
            "price_precision": {"USDT": 8, "IRT": 4},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.DOGE: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.XRP: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.ADA: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.FTM: {
            "quantity_precision": 2,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.LINK: {
            "quantity_precision": 2,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.UNI: {
            "quantity_precision": 2,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.MKR: {
            "quantity_precision": 4,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.SAND: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.AAVE: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.DOT: {
            "quantity_precision": 2,
            "price_precision": {"USDT": 3, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.BCH: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.MANA: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": False
        },
        NobitexSymbol.GMT: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.EOS: {
            "quantity_precision": 2,
            "price_precision": {"USDT": 4, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.AXS: {
            "quantity_precision": 5,
            "price_precision": {"USDT": 2, "IRT": 0},
            "minimum_quantity": 1,
            "is_active": True
        },
        NobitexSymbol.USDT: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 0.1,
            "is_active": True
        },
        NobitexSymbol.AVAX: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 0.1,
            "is_active": True
        },
        NobitexSymbol.PMN: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 0.1,
            "is_active": True
        },
        NobitexSymbol.XLM: {
            "quantity_precision": 1,
            "price_precision": {"USDT": 5, "IRT": 0},
            "minimum_quantity": 0.1,
            "is_active": True
        }
    }
    
    FEES = {
        "USDT": 0.0025,
        "IRT": 0.0035,
        "OTC": 0.0035
    }
    
    CAPITAL_USDT = 4
    ACCEPTABLE_MARGIN = 0.05