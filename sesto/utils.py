import MetaTrader5 as mt5
from sesto.constants import CRYPTOCURRENCIES, OILS, METALS, CURRENCY_PAIRS
def get_price_at_pnl(pnl_multiplier: float, order_commission: float, position_size_usd: float, leverage: float, entry_price: float, type: str) -> float:
    required_movement = pnl_multiplier + (order_commission / position_size_usd)
    price_movement = required_movement / leverage

    if type == 'long':
        target_price = entry_price * (1 + price_movement)
    elif type == 'short':
        target_price = entry_price * (1 - price_movement)
    else:
        raise ValueError(f"Unknown trade type: {type}")

    return target_price  # Ensure target_price is at least 1% of entry_price

def get_pnl_at_price(current_price: float, entry_price: float, position_size_usd: float, leverage: float, type: str) -> float:
    if type == 'long':
        price_change = (current_price - entry_price) / entry_price
    elif type == 'short':
        price_change = (entry_price - current_price) / entry_price
    else:
        raise ValueError(f"Unknown trade type: {type}")
    
    # Calculate the PNL as a percentage of the position size
    pnl = position_size_usd * price_change
    return pnl

def calculate_position_size(capital: float, leverage: float) -> float:
    return capital * leverage

def calculate_commission(position_size_usd: float, pair) -> float:
    """
    Calculate the total commission for a trade based on the notional value.
    :param position_size_usd: The notional value of the position in USD.
    :return: The total commission for opening and closing the trade.
    """
    if pair in CRYPTOCURRENCIES:
        commission_rate = 0.0005 # 0.05%
    elif pair in OILS:
        commission_rate = 0.0001 # 0.01%
    elif pair in METALS:
        commission_rate = 0.0001 # 0.01%
    elif pair in CURRENCY_PAIRS:
        commission_rate = 0.0005 # 0.05%

    commission = position_size_usd * commission_rate # Total commission for both open and close
    return commission

def calculate_break_even_price(entry_price: float, order_commission: float, position_size_usd: float, type: str) -> float:
    if type == 'long':
        return entry_price * (1 + (order_commission / position_size_usd))
    elif type == 'short':
        return entry_price * (1 - (order_commission / position_size_usd))
    else:
        raise ValueError(f"Unknown position type: {type}")

def calculate_price_with_spread(price: float, spread_multiplier: float, increase: bool) -> float:
    if increase:
        return price * (1 + spread_multiplier)
    else:
        return price * (1 - spread_multiplier)
    
def calculate_liquidation_price(entry_price: float, leverage: float, type: str) -> float:
    if type == 'long':
        liq_p = entry_price * (1 - (1 / leverage))
    elif type == 'short':
        liq_p = entry_price * (1 + (1 / leverage))
    else:
        raise ValueError(f"Unknown position type: {type}")
    
    return liq_p

def convert_lots_to_usd(symbol, lots, price_open):
    """
    Convert volume size from lots to USD amount.
    
    :param symbol: The trading symbol (e.g., 'BITCOIN', 'ETHEREUM')
    :param lots: The volume size in lots
    :return: The equivalent USD amount
    """
    # Get the contract size for the symbol
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise ValueError(f"Symbol {symbol} not found in MetaTrader 5")
    
    contract_size = symbol_info.trade_contract_size
    
    # Calculate the USD amount using the opening price
    usd_amount = lots * contract_size * price_open
    
    return usd_amount

def calculate_trade_volume(open_price: float, current_price: float, current_pnl: float, leverage: float) -> float:
    """
    Calculate the trade volume given the open price, current price, current PNL, and leverage.

    :param open_price: The opening price of the trade
    :param current_price: The current price of the asset
    :param current_pnl: The current profit/loss of the trade in USD
    :param leverage: The leverage used for the trade
    :return: The volume of the trade in USD
    """
    price_change = abs(current_price - open_price) / open_price
    trade_volume = abs(current_pnl / (price_change * leverage))
    return trade_volume

def convert_usd_to_lots(symbol: str, usd_amount: float, current_price: float) -> float:
    """
    Convert USD amount to lots for a given symbol.

    :param symbol: The trading symbol (e.g., 'BITCOIN', 'ETHEREUM')
    :param usd_amount: The amount in USD to convert
    :param current_price: The current price of the asset
    :return: The equivalent amount in lots
    """
    # Get the symbol information
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise ValueError(f"Symbol {symbol} not found in MetaTrader 5")
    
    # Get the contract size and calculate lots
    contract_size = symbol_info.trade_contract_size
    lots = usd_amount / (contract_size * current_price)
    
    # Round to the nearest lot step
    lot_step = symbol_info.volume_step
    lots = round(lots / lot_step) * lot_step
    
    return lots