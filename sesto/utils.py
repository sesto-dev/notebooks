def get_price_at_pnl(pnl_percentage: float, order_fee: float, position_size_usd: float, leverage: float, entry_price: float, type: str) -> float:
    required_movement = (pnl_percentage / 100) + (order_fee / position_size_usd)
    price_movement = required_movement / leverage

    if type == 'long':
        target_price = entry_price * (1 + price_movement)
    elif type == 'short':
        target_price = entry_price * (1 - price_movement)
    else:
        raise ValueError(f"Unknown trade type: {type}")

    return target_price

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