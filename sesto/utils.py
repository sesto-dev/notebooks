def get_price_at_pnl(desired_pnl: float, entry_price: float, position_size_usd: float, leverage: float, type: str, commission: float) -> tuple:
    """
    Calculate the price at which the desired PnL is achieved, with and without commission.

    :param desired_pnl: The desired profit or loss in USD.
    :param entry_price: The entry price of the trade.
    :param position_size_usd: The size of the position in USD.
    :param leverage: The leverage used for the trade.
    :param type: The type of position, either 'long' or 'short'.
    :param commission: The commission in USD.
    :return: A tuple containing two prices:
             - Price with commission
             - Price without commission
    :raises ValueError: If an unknown trade type is provided.
    """
    if type == 'long':
        price_including_commission = entry_price * (1 + (desired_pnl + commission) / position_size_usd)
        price_excluding_commission = entry_price * (1 + desired_pnl / position_size_usd)
    elif type == 'short':
        price_including_commission = entry_price * (1 - (desired_pnl + commission) / position_size_usd)
        price_excluding_commission = entry_price * (1 - desired_pnl / position_size_usd)
    else:
        raise ValueError(f"Unknown trade type: {type}")

    return price_including_commission, price_excluding_commission

def get_pnl_at_price(current_price: float, entry_price: float, position_size_usd: float, leverage: float, type: str, commission: float) -> tuple:
    if type == 'long':
        price_change = (current_price - entry_price) / entry_price
    elif type == 'short':
        price_change = (entry_price - current_price) / entry_price
    else:
        raise ValueError(f"Unknown trade type: {type}")
    
    # Calculate gross PNL
    pnl_including_commission = position_size_usd * price_change

    # Subtract commissions
    pnl_excluding_commission = pnl_including_commission - commission
    return pnl_including_commission, pnl_excluding_commission

def calculate_position_size(capital: float, leverage: float) -> float:
    return capital * leverage

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

