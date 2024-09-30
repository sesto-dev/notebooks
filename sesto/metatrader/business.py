import MetaTrader5 as mt5
import pandas as pd

# Initialize and connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()
else:
    print("MetaTrader5 initialized successfully")

def send_market_order(symbol, volume, order_type, sl=0.0, tp=0.0,
                      deviation=20, comment='', magic=0, type_filling=mt5.ORDER_FILLING_IOC):
    if order_type not in ['buy', 'sell']:
        print(f"Invalid order_type: {order_type}. Must be 'buy' or 'sell'.")
        return None

    if volume <= 0:
        print("Volume must be greater than 0.")
        return None

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick for symbol: {symbol}")
        return None

    order_type_dict = {'buy': mt5.ORDER_TYPE_BUY, 'sell': mt5.ORDER_TYPE_SELL}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    if price_dict[order_type] == 0.0:
        print(f"Invalid price retrieved for symbol: {symbol} and order_type: {order_type}")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_dict[order_type],
        "price": price_dict[order_type],
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    order_result = mt5.order_send(request)

    if order_result is None:
        print(f"Order failed, error code: {mt5.last_error()}")
        return None
    elif order_result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed, retcode: {order_result.retcode}")
        return None
    
    print(f"Order successfully placed: {order_result}")
    return order_result


def close_position(position, deviation=20, magic=0, comment='', type_filling=mt5.ORDER_FILLING_IOC):
    if 'type' not in position or 'ticket' not in position:
        print("Position dictionary missing 'type' or 'ticket' keys.")
        return None

    order_type_dict = {
        0: mt5.ORDER_TYPE_BUY,   # Corrected
        1: mt5.ORDER_TYPE_SELL   # Corrected
    }

    position_type = position['type']
    if position_type not in order_type_dict:
        print(f"Unknown position type: {position_type}")
        return None

    price_dict = {
        0: mt5.symbol_info_tick(position['symbol']).ask,  # Buy order uses Ask price
        1: mt5.symbol_info_tick(position['symbol']).bid   # Sell order uses Bid price
    }

    tick = mt5.symbol_info_tick(position['symbol'])
    if tick is None:
        print(f"Failed to get tick for symbol: {position['symbol']}")
        return None

    price = price_dict[position_type]
    if price == 0.0:
        print(f"Invalid price retrieved for symbol: {position['symbol']}")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position['ticket'],  # select the position you want to close
        "symbol": position['symbol'],
        "volume": position['volume'],  # FLOAT
        "type": order_type_dict[position_type],
        "price": price,
        "deviation": deviation,  # INTEGER
        "magic": magic,          # INTEGER
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }

    order_result = mt5.order_send(request)

    if order_result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to close position {position['ticket']}: {order_result.comment}")
        return None

    print(f"Position {position['ticket']} closed successfully.")
    return order_result


def close_all_positions(order_type='all', magic=None, type_filling=mt5.ORDER_FILLING_IOC):
    order_type_dict = {
        'buy': mt5.ORDER_TYPE_BUY,
        'sell': mt5.ORDER_TYPE_SELL
    }

    if mt5.positions_total() > 0:
        positions = mt5.positions_get()
        if positions is None:
            print("Failed to retrieve positions.")
            return []

        positions_data = [pos._asdict() for pos in positions]
        positions_df = pd.DataFrame(positions_data)

        # Filtering by magic if specified
        if magic is not None:
            positions_df = positions_df[positions_df['magic'] == magic]

        # Filtering by order_type if not 'all'
        if order_type != 'all':
            if order_type not in order_type_dict:
                print(f"Invalid order_type: {order_type}. Must be 'buy', 'sell', or 'all'.")
                return []
            positions_df = positions_df[positions_df['type'] == order_type_dict[order_type]]

        if positions_df.empty:
            print('No open positions matching the criteria.')
            return []

        results = []
        for _, position in positions_df.iterrows():
            order_result = close_position(position, type_filling=type_filling)
            if order_result:
                results.append(order_result)
            else:
                print(f"Failed to close position {position['ticket']}.")
        
        return results
    else:
        print("No open positions to close.")
        return []


def modify_sl_tp(ticket, stop_loss, take_profit):
    if not isinstance(ticket, int):
        print("Ticket must be an integer.")
        return None

    try:
        stop_loss = float(stop_loss)
        take_profit = float(take_profit)
    except ValueError:
        print("Stop loss and take profit must be numbers.")
        return None

    request = {
        'action': mt5.TRADE_ACTION_SLTP,
        'position': ticket,
        'sl': stop_loss,
        'tp': take_profit
    }

    res = mt5.order_send(request)

    if res.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to modify SL/TP for ticket {ticket}: {res.comment}")
        return None

    print(f"SL/TP modified for ticket {ticket} successfully.")
    return res

def get_positions(magic=None):
    total_positions = mt5.positions_total()
    if total_positions > 0:
        positions = mt5.positions_get()
        if positions is None:
            print("Failed to retrieve positions.")
            return pd.DataFrame()

        positions_data = [pos._asdict() for pos in positions]
        positions_df = pd.DataFrame(positions_data)

        if magic is not None:
            positions_df = positions_df[positions_df['magic'] == magic]

        return positions_df
    else:
        print("No open positions found.")
        return pd.DataFrame(columns=['ticket', 'time', 'time_msc', 'time_update', 'time_update_msc', 'type',
                                     'magic', 'identifier', 'reason', 'volume', 'price_open', 'sl', 'tp',
                                     'price_current', 'swap', 'profit', 'symbol', 'comment', 'external_id'])