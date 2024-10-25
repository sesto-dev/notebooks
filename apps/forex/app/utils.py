from constants import CRYPTOCURRENCIES, OILS, METALS, CURRENCY_PAIRS
from api.data import symbol_info

def convert_lots_to_usd(symbol, lots, price_open):
    """
    Convert volume size from lots to USD amount.
    
    :param symbol: The trading symbol (e.g., 'BITCOIN', 'ETHEREUM')
    :param lots: The volume size in lots
    :return: The equivalent USD amount
    """
    # Get the contract size for the symbol
    symbol_info = symbol_info(symbol)
    if symbol_info is None:
        raise ValueError(f"Symbol {symbol} not found in MetaTrader 5")
    
    contract_size = symbol_info.trade_contract_size
    
    # Calculate the USD amount using the opening price
    usd_amount = lots * contract_size * price_open
    
    return usd_amount

def convert_usd_to_lots(symbol: str, usd_amount: float, current_price: float) -> float:
    """
    Convert USD amount to lots for a given symbol.

    :param symbol: The trading symbol (e.g., 'BITCOIN', 'ETHEREUM')
    :param usd_amount: The amount in USD to convert
    :param current_price: The current price of the asset
    :return: The equivalent amount in lots
    """
    # Get the symbol information
    symbol_info = symbol_info(symbol)
    if symbol_info is None:
        raise ValueError(f"Symbol {symbol} not found in MetaTrader 5")
    
    # Get the contract size and calculate lots
    contract_size = symbol_info.trade_contract_size
    lots = usd_amount / (contract_size * current_price)
    
    # Round to the nearest lot step
    lot_step = symbol_info.volume_step
    lots = round(lots / lot_step) * lot_step
    
    return lots

def calculate_commission(position_size_usd: float, pair) -> float:
    """
    Calculate the total commission for a trade based on the notional value.
    :param position_size_usd: The notional value of the position in USD.
    :return: The total commission for opening and closing the trade.
    """
    if pair in CRYPTOCURRENCIES:
        commission_rate = 0.0005 # 0.05%
    elif pair in OILS:
        commission_rate = 0.00025
    elif pair in METALS:
        commission_rate = 0.00025
    elif pair in CURRENCY_PAIRS:
        commission_rate = 0.00025
    else:
        # Throw exception
        raise ValueError(f"Could not calculate commission for unknown pair: {pair}")

    commission = position_size_usd * commission_rate # Total commission for both open and close
    return commission