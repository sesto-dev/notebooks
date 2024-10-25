import logging
from time import sleep
from datetime import datetime, timedelta
import pandas as pd

from utils import calculate_commission, convert_lots_to_usd, convert_usd_to_lots
from constants import CRYPTOCURRENCIES, TIMEZONE, MT5Timeframe
from config import TRAILING_STOP_STEPS, PAIRS, MAIN_TIMEFRAME, TP_PNL_MULTIPLIER, SL_PNL_MULTIPLIER, LEVERAGE, DEVIATION, VOLUME

from algorithms.utils import get_price_at_pnl, calculate_position_size, get_pnl_at_price, calculate_trade_volume
from algorithms.fractal import fractal
from library.telegram import TelegramSender

from api.business import get_positions, send_market_order, modify_sl_tp, get_order_from_ticket, get_deal_from_ticket
from api.data import symbol_info_tick, symbol_info, fetch_data_pos

logger = logging.getLogger(__name__)

Telegram = TelegramSender()

def calculate_position_capital(symbol, volume_lots, leverage, price_open):
    position_size_usd = convert_lots_to_usd(symbol, volume_lots, price_open)
    capital_used = position_size_usd / leverage
    return capital_used

def have_open_positions_in_symbol(symbol):
    positions = get_positions()
    return symbol in positions['symbol'].values

def market_is_open(symbol):
    if symbol not in CRYPTOCURRENCIES:
        return True
    else:
    # Check whether the market is open, if its a crypto then market doesn't close
        tick = symbol_info_tick(symbol)
        if tick is not None:
            tick_time = datetime.fromtimestamp(tick.time, tz=TIMEZONE)
            current_time = datetime.now(TIMEZONE)
            time_difference = current_time - tick_time

            if time_difference > timedelta(minutes=5):
                return False
            else:
                return True
        else:
            return False

# dict to store trades, keys are position tickets, values are the entire position object
trades = {}

def check_entry_condition():
    """
    Continuously monitors for fractal signals and places market orders accordingly.
    """
    while True:
        try:
            for pair in PAIRS:
                if have_open_positions_in_symbol(pair):
                    continue

                if not market_is_open(pair):
                    continue

                df = fetch_data_pos(pair, MAIN_TIMEFRAME, 50)
                if df is None or df.empty:
                    print(f"No data fetched for {pair}. Skipping...")
                    continue

                df['fractal'] = fractal(df)

                last_tick_price = symbol_info_tick(pair).ask
                if last_tick_price is None:
                    print(f"Failed to retrieve ask price for {pair}.")
                    continue

                position_capital = calculate_position_capital(pair, VOLUME, LEVERAGE, last_tick_price)
                desired_sl_pnl = position_capital * SL_PNL_MULTIPLIER
                position_size = calculate_position_size(position_capital, LEVERAGE)
                commission = calculate_commission(position_size_usd=position_size, pair=pair)

                last_row = df.iloc[-2]
                current_time = datetime.now(TIMEZONE).replace(microsecond=0)

                if last_row['fractal'] in ['top', 'bottom']:
                    sl_including_commission, sl_excluding_commission = get_price_at_pnl(
                        desired_pnl=desired_sl_pnl,
                        commission=commission,
                        position_size_usd=position_size,
                        leverage=LEVERAGE,
                        entry_price=last_tick_price,
                        type='long' if last_row['fractal'] == 'bottom' else 'short'
                    )
                    
                    order = send_market_order(
                        symbol=pair,
                        volume=VOLUME,
                        order_type='sell' if last_row['fractal'] == 'top' else 'buy',
                        sl=sl_including_commission,
                        deviation=DEVIATION,
                        type_filling='ORDER_FILLING_FOK'
                    )

                    if order is not None:
                        trade_info = {
                            'event': 'trade_opened',
                            'symbol': pair,
                            'entry_condition': f"{last_row['fractal'].upper()} FRACTAL DETECTED",
                            'position_capital': f"${position_capital:.5f}",
                            'position_size': f"${position_size:.5f}",
                            'sl_pnl_multiplier': f"{SL_PNL_MULTIPLIER * 100}%",
                            'desired_sl_pnl': f"${desired_sl_pnl:.5f}",
                            'commission': f"${commission:.5f}",
                            'order_info': {
                                'order_price': f"${order.price:.5f}",
                                'order_volume': f"{order.volume:.5f}",
                                'type': 'long' if last_row['fractal'] == 'bottom' else 'short',
                                "sl": sl_including_commission,
                            },
                            'market_info': {
                                'row_close': f"${last_row['close']:.5f}",
                                'last_tick_price': f"${last_tick_price:.5f}",
                            },
                            'sl_including_commission': {
                                'sl_including_commission': f"${sl_including_commission:.5f}",
                                'sl_price_difference_including_commission': f"${(sl_including_commission - last_tick_price):.5f}",
                                'sl_price_difference_percentage_including_commission': f"{(sl_including_commission / last_tick_price - 1) * 100:.5f}%",
                                'pnl_at_sl_including_commission': f"${get_pnl_at_price(sl_including_commission, last_tick_price, position_size, LEVERAGE, 'long' if last_row['fractal'] == 'bottom' else 'short', commission)[1]:.5f}",
                            },
                            'sl_excluding_commission': {
                                'sl_excluding_commission': f"${sl_excluding_commission:.5f}",
                                'sl_price_difference_excluding_commission': f"${(sl_excluding_commission - last_tick_price):.5f}",
                                'sl_price_difference_percentage_excluding_commission': f"{(sl_excluding_commission / last_tick_price - 1) * 100:.5f}%",
                                'pnl_at_sl_excluding_commission': f"${get_pnl_at_price(sl_excluding_commission, last_tick_price, position_size, LEVERAGE, 'long' if last_row['fractal'] == 'bottom' else 'short', commission)[1]:.5f}",
                            },
                        }

                        
                        Telegram.send_json_message(trade_info)
                        logger.info(f"Order placed successfully for {pair}: {trade_info}")
                    else:
                        trade_info = {
                            'event': 'trade_failed_to_open',
                            'entry_condition': f"{last_row['fractal'].upper()} FRACTAL DETECTED",
                            'symbol': pair,
                            'type': 'long' if last_row['fractal'] == 'bottom' else 'short',
                            'position_capital': f"${position_capital:.5f}",
                            'position_volume': f"{VOLUME} lots",
                            'position_size': f"${position_size:.5f}",
                            'sl_pnl_multiplier': f"{SL_PNL_MULTIPLIER * 100}%",
                            'desired_sl_pnl': f"${desired_sl_pnl:.5f}",
                            'commission': f"${commission:.5f}",
                            'market_info': {
                                'row_close': f"${last_row['close']:.5f}",
                                'last_tick_price': f"${last_tick_price:.5f}",
                            },
                            'sl_including_commission': {
                                'sl_including_commission': f"${sl_including_commission:.5f}",
                                'sl_price_difference_including_commission': f"${(sl_including_commission - last_tick_price):.5f}",
                                'sl_price_difference_percentage_including_commission': f"{(sl_including_commission / last_tick_price - 1) * 100:.5f}%",
                                'pnl_at_sl_including_commission': f"${get_pnl_at_price(sl_including_commission, last_tick_price, position_size, LEVERAGE, 'long' if last_row['fractal'] == 'bottom' else 'short', commission)[1]:.5f}",
                            },
                            'sl_excluding_commission': {
                                'sl_excluding_commission': f"${sl_excluding_commission:.5f}",
                                'sl_price_difference_excluding_commission': f"${(sl_excluding_commission - last_tick_price):.5f}",
                                'sl_price_difference_percentage_excluding_commission': f"{(sl_excluding_commission / last_tick_price - 1) * 100:.5f}%",
                                'pnl_at_sl_excluding_commission': f"${get_pnl_at_price(sl_excluding_commission, last_tick_price, position_size, LEVERAGE, 'long' if last_row['fractal'] == 'bottom' else 'short', commission)[1]:.5f}",
                            },
                        }
                        Telegram.send_json_message(trade_info)
            # Calculate next run time aligned to the next 15-minute interval
            now = datetime.now(TIMEZONE)
            next_run = (now + timedelta(minutes=15 - now.minute % 15)).replace(second=0, microsecond=0)
            sleep_time = (next_run - now).total_seconds() + 2  # Add 2 seconds buffer

            print(f"{datetime.now(tz=TIMEZONE)} - Waiting for {sleep_time} seconds until next 15-minute check.")
            sleep(sleep_time)
        
        except Exception as e:
            import traceback
            error_msg = f"Exception in monitor_open_trades: {e}\n{traceback.format_exc()}"
            print(error_msg)
            Telegram.send_json_message({"error": error_msg})
            sleep(10)

def monitor_open_trades():
    """
    Continuously monitors open trades, detects closed trades, and sends notifications.
    Utilizes a cached state to detect changes in open positions.
    """
    cached_positions = {}

    while True:
        try:
            current_time = datetime.now(TIMEZONE).replace(microsecond=0)

            positions = get_positions()
            if positions.empty:
                positions = pd.DataFrame(columns=[
                    'ticket', 'time', 'time_msc', 'time_update', 'time_update_msc', 'type',
                    'magic', 'identifier', 'reason', 'volume', 'price_open', 'sl', 'tp',
                    'price_current', 'swap', 'profit', 'symbol', 'comment', 'external_id'
                ])

            positions['time'] = pd.to_datetime(positions['time'], unit='s', utc=True)
            positions['time_update'] = pd.to_datetime(positions['time_update'], unit='s', utc=True)

            # Detect closed trades by comparing cached_positions with current positions
            current_tickets = set(positions['ticket'].values)
            cached_tickets = set(cached_positions.keys())

            # Identify closed tickets
            closed_tickets = cached_tickets - current_tickets

            for ticket in closed_tickets:
                position = cached_positions.pop(ticket)
                sleep(2)
                closed_order = get_order_from_ticket(ticket)
                if closed_order:
                    closed_order['event'] = 'trade_closed_order'
                    # Telegram.send_json_message(closed_order)

                closed_deal = get_deal_from_ticket(ticket)
                if closed_deal:
                    closed_deal['event'] = 'trade_closed_deal'
                    Telegram.send_json_message(closed_deal)
                else:
                    # Convert position to a dictionary with meaningful keys
                    position_dict = {
                        'ticket': position.ticket if hasattr(position, 'ticket') else 'N/A',
                        'time': position.time if hasattr(position, 'time') else 'N/A',
                        'type': position.type if hasattr(position, 'type') else 'N/A',
                        'symbol': position.symbol if hasattr(position, 'symbol') else 'N/A',
                        'volume': position.volume if hasattr(position, 'volume') else 'N/A',
                        'price_open': position.price_open if hasattr(position, 'price_open') else 'N/A',
                        'sl': position.sl if hasattr(position, 'sl') else 'N/A',
                        'tp': position.tp if hasattr(position, 'tp') else 'N/A',
                        'price_current': position.price_current if hasattr(position, 'price_current') else 'N/A',
                        'swap': position.swap if hasattr(position, 'swap') else 'N/A',
                        'profit': position.profit if hasattr(position, 'profit') else 'N/A',
                    }
                    Telegram.send_json_message({
                        "error": "Position Closed but failed to get deal from ticket", 
                        'cached_position': position_dict,
                        'position_type': str(type(position)),
                        'position_dir': str(dir(position))
                    })

            # Update cached_positions with current positions
            for index, position in positions.iterrows():
                cached_positions[position.ticket] = position

                # Check if the position ticket exists in trades dict
                if position.ticket not in trades:
                    trades[position.ticket] = position
                else:
                    # Check if position has changed
                    if not trades[position.ticket].equals(position):
                        trades[position.ticket] = position

                # Calculate the actual capital used for this trade
                position_capital = calculate_position_capital(
                    position.symbol, position.volume, LEVERAGE, position.price_open
                )
                position_size = calculate_position_size(position_capital, LEVERAGE)
                commission = calculate_commission(position_size_usd=position_size, pair=position.symbol)
                current_pnl_percentage = (position.profit / position_capital) * 100
                current_sl_pnl_including_commission, current_sl_pnl_excluding_commission = get_pnl_at_price(
                    position.sl, position.price_open, position_size, LEVERAGE,
                    'long' if position.type == 0 else 'short', commission
                )

                for trailing_step in TRAILING_STOP_STEPS:
                    trigger_pnl_multiplier = trailing_step['trigger_pnl_multiplier']
                    new_sl_pnl_multiplier = trailing_step['new_sl_pnl_multiplier']
                    trigger_pnl = position_capital * trigger_pnl_multiplier
                    new_sl_pnl = position_capital * new_sl_pnl_multiplier

                    trigger_price_including_commission, trigger_price_excluding_commission = get_price_at_pnl(
                        desired_pnl=trigger_pnl,
                        commission=commission,
                        position_size_usd=position_size,
                        leverage=LEVERAGE,
                        entry_price=position.price_open,
                        type='long' if position.type == 0 else 'short'
                    )
         
                    new_sl_price_including_commission, new_sl_price_excluding_commission = get_price_at_pnl(
                        desired_pnl=new_sl_pnl,
                        commission=commission,
                        position_size_usd=position_size,
                        leverage=LEVERAGE,
                        entry_price=position.price_open,
                        type='long' if position.type == 0 else 'short'
                    )          

                    trigger_pnl_including_commission, trigger_pnl_excluding_commission = get_pnl_at_price(
                        current_price=trigger_price_including_commission,
                        entry_price=position.price_open,
                        position_size_usd=position_size,
                        leverage=LEVERAGE,
                        type='long' if position.type == 0 else 'short',
                        commission=commission
                    )
        
                    pnl_at_new_sl_including_commission, pnl_at_new_sl_excluding_commission = get_pnl_at_price(
                        current_price=new_sl_price_including_commission,
                        entry_price=position.price_open,
                        position_size_usd=position_size,
                        leverage=LEVERAGE,
                        type='long' if position.type == 0 else 'short',
                        commission=commission
                    )
               
                    if position.profit is not None and trigger_pnl_including_commission is not None and position.profit >= trigger_pnl_including_commission:
                        if position.sl is not None and new_sl_price_including_commission is not None:
                            if (position.type == 0 and new_sl_price_including_commission > position.sl) or (position.type == 1 and new_sl_price_including_commission < position.sl):
                                sl_info = {
                                    'event': 'trailing_stop_triggered',
                                    'position_data': {
                                        'symbol': position.symbol,
                                        'trade_open_date': position.time.isoformat(),
                                        'type': 'long' if position.type == 0 else 'short',
                                        'entry_price': f"${position.price_open:.5f}",
                                        'current_price': f"${position.price_current:.5f}",
                                        'capital_used': f"${position_capital:.5f}",
                                        'position_size': f"${position_size:.5f}",
                                        'deduced_volume': f"${calculate_trade_volume(position.price_open, position.price_current, position.profit, LEVERAGE):.5f}",
                                        'deduced_volume_lots': f"${convert_usd_to_lots(position.symbol, calculate_trade_volume(position.price_open, position.price_current, position.profit, LEVERAGE), position.price_current):.5f}",
                                        'commission': f"${commission:.5f}",
                                    },
                                    'trigger_data': {
                                        'trigger_price': f"${trigger_price_including_commission:.5f}",
                                        'trigger_pnl': f"${trigger_pnl_including_commission:.5f}",
                                        'trigger_pnl_percentage': f"{(trigger_pnl_including_commission / position_capital) * 100:.5f}%",
                                        'trigger_price_excluding_commission': f"${trigger_price_excluding_commission:.5f}",
                                        'trigger_pnl_excluding_commission': f"${trigger_pnl_excluding_commission:.5f}",
                                        'trigger_pnl_excluding_commission_percentage': f"{(trigger_pnl_excluding_commission / position_capital) * 100:.5f}%",
                                    },
                                    'current_pnl': {
                                        'current_pnl': f"${position.profit:.5f}",
                                        'current_pnl_percentage': f"{current_pnl_percentage:.5f}%",
                                    },
                                    'old_sl': {
                                        'old_sl': f"${position.sl:.5f}",
                                        'pnl_at_old_sl': f"${current_sl_pnl_including_commission:.5f}",
                                        'old_sl_pnl_percentage': f"{(current_sl_pnl_including_commission / position_capital) * 100:.5f}%",
                                    },
                                    'new_sl': {
                                        'new_sl': f"${new_sl_price_including_commission:.5f}",
                                        'pnl_at_new_sl': f"${pnl_at_new_sl_including_commission:.5f}",
                                        'new_sl_pnl_percentage': f"{(pnl_at_new_sl_including_commission / position_capital) * 100:.5f}%",
                                        'new_sl_excluding_commission': f"${new_sl_price_excluding_commission:.5f}",
                                        'pnl_at_new_sl_excluding_commission': f"${pnl_at_new_sl_excluding_commission:.5f}",
                                        'new_sl_pnl_excluding_commission_percentage': f"{(pnl_at_new_sl_excluding_commission / position_capital) * 100:.5f}%",
                                    }
                                }

                                modify_request = modify_sl_tp(position.ticket, new_sl_price_including_commission, position.tp)
                                if modify_request is not None:
                                    Telegram.send_json_message(sl_info)
                                break  # Exit the trailing steps loop after modification
                        # else:
                            # print(f"Warning: Stop Loss is None for position {position.ticket}")
                    # else:
                        # print(f"Warning: Profit or trigger PNL is None for position {position.ticket}")

            sleep(10)

        except Exception as e:
            import traceback
            error_msg = f"Exception in monitor_open_trades: {e}\n{traceback.format_exc()}"
            print(error_msg)
            Telegram.send_json_message({"error": error_msg})
            sleep(10)