import MetaTrader5 as mt5

def get_price_at_pnl(pnl_multiplier: float, order_fee: float, position_size_usd: float, leverage: float, entry_price: float, type: str) -> float:
    required_movement = pnl_multiplier + (order_fee / position_size_usd)
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

def calculate_fee(position_size_usd: float) -> float:
    order_fee = (position_size_usd / 1000000) * 16 * 2
    return order_fee

def calculate_break_even_price(entry_price: float, order_fee: float, position_size_usd: float, type: str) -> float:
    if type == 'long':
        return entry_price * (1 + (order_fee / position_size_usd))
    elif type == 'short':
        return entry_price * (1 - (order_fee / position_size_usd))
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