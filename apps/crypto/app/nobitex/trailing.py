import sys
sys.path.append("../../..")

from time import sleep
from datetime import datetime  # Add this line
import json
import os
from dotenv import load_dotenv
import concurrent.futures

from sesto.nobitex.client import NobitexClient
from sesto.nobitex.endpoints import NobitexEndpoints
from sesto.telegram import TelegramSender

from sesto.utils import calculate_position_size, get_pnl_at_price, get_price_at_pnl
from sesto.nobitex.utils import calculate_nobitex_commission
load_dotenv()

TRAILING_STOP_STEPS = [
    {'trigger_pnl_multiplier': 4.00, 'new_sl_pnl_multiplier': 3.50},
    {'trigger_pnl_multiplier': 3.50, 'new_sl_pnl_multiplier': 3.00},
    {'trigger_pnl_multiplier': 3.00, 'new_sl_pnl_multiplier': 2.75},
    {'trigger_pnl_multiplier': 2.75, 'new_sl_pnl_multiplier': 2.50},
    {'trigger_pnl_multiplier': 2.50, 'new_sl_pnl_multiplier': 2.25},
    {'trigger_pnl_multiplier': 2.25, 'new_sl_pnl_multiplier': 2.00},
    {'trigger_pnl_multiplier': 2.00, 'new_sl_pnl_multiplier': 1.75},
    {'trigger_pnl_multiplier': 1.75, 'new_sl_pnl_multiplier': 1.50},
    {'trigger_pnl_multiplier': 1.50, 'new_sl_pnl_multiplier': 1.25},
    {'trigger_pnl_multiplier': 1.25, 'new_sl_pnl_multiplier': 1.00},
    {'trigger_pnl_multiplier': 1.00, 'new_sl_pnl_multiplier': 0.75},
    {'trigger_pnl_multiplier': 0.75, 'new_sl_pnl_multiplier': 0.45},
    {'trigger_pnl_multiplier': 0.50, 'new_sl_pnl_multiplier': 0.22},
    {'trigger_pnl_multiplier': 0.25, 'new_sl_pnl_multiplier': 0.12},
    {'trigger_pnl_multiplier': 0.12, 'new_sl_pnl_multiplier': 0.05},
    {'trigger_pnl_multiplier': 0.06, 'new_sl_pnl_multiplier': 0.025},
]
# Jupyter Notebook cell 1: Import necessary modules and set up the client
api_keys = [
    os.getenv("NOBITEX_API_KEY_A"),
    os.getenv("NOBITEX_API_KEY_H"),
]

clients = [NobitexClient(api_key) for api_key in api_keys]

def run_strategy_for_client(client):
    def get_stop_loss_order(src_currency, dst_currency):
        for order in orders['orders']:
            isSrcCurrencyMatch = order['srcCurrency'].lower() == src_currency.lower()
            isDstCurrencyMatch = order['dstCurrency'].lower() == dst_currency.lower() or (dst_currency.lower() == 'usdt' and order['dstCurrency'].lower() == 'tether')
            if order['execution'] == 'StopLimit' and isSrcCurrencyMatch and isDstCurrencyMatch:
                return order
        return None

    while True:
        positions = client.get_positions()
        orders = client.get_my_orders()

        for position in positions['positions']:
            symbol = position['srcCurrency'] + position['dstCurrency']
            created_at = datetime.fromisoformat(position['createdAt'])
            leverage=float(position['leverage'])
            entryPrice=float(position['entryPrice'])
            sl_order = get_stop_loss_order(position['srcCurrency'], position['dstCurrency'])
            collateral = float(position['collateral'])
            unrealized_pnl = float(position['unrealizedPNL'])
            trade_size = calculate_position_size(collateral, leverage)
            fee = calculate_nobitex_commission(position_size_usd=trade_size) 
            
            current_pnl_percentage = (unrealized_pnl / collateral) * 100
            print(f"{created_at} - {symbol} - PNL INFO - PNL: ${unrealized_pnl:.3f} or {current_pnl_percentage:.3f}%")

            if sl_order:
                sl_price = float(sl_order['price'])
                current_sl_pnl = get_pnl_at_price(sl_price, entryPrice, trade_size, leverage, 'long' if position['side'] == 'buy' else 'short')
                current_sl_pnl_percentage = (current_sl_pnl / collateral) * 100
                print(f"{created_at} - {symbol} - POSITION INFO - OPEN PRICE: ${entryPrice:.3f} - TRADE CAPITAL: ${collateral:.3f} - CURRENT SL: ${sl_price:.3f}")        
                print(f"{created_at} - {symbol} - SL PNL INFO - PNL AT CURRENT SL: ${current_sl_pnl:.3f} or {current_sl_pnl_percentage:.3f}%")
            
            
            for trailing_step in TRAILING_STOP_STEPS:
                trigger_pnl_multiplier = trailing_step['trigger_pnl_multiplier']
                new_sl_pnl_multiplier = trailing_step['new_sl_pnl_multiplier']

                price_at_trigger_pnl_multiplier = get_price_at_pnl(
                    pnl_multiplier=trigger_pnl_multiplier,
                    order_fee=fee,
                    position_size_usd=trade_size,
                    leverage=leverage,
                    entry_price=entryPrice,
                    type='long' if position['side'] == 'buy' else 'short'
                )
                new_sl_at_new_sl_pnl_multiplier = get_price_at_pnl(
                    pnl_multiplier=new_sl_pnl_multiplier,
                    order_fee=fee,
                    position_size_usd=trade_size,
                    leverage=leverage,
                    entry_price=entryPrice,
                    type='long' if position['side'] == 'buy' else 'short'
                )
                pnl_at_trigger = get_pnl_at_price(
                    price_at_trigger_pnl_multiplier,
                    entryPrice,
                    trade_size,
                    leverage,
                    'long' if position['side'] == 'buy' else 'short'
                )
                pnl_at_new_sl = get_pnl_at_price(
                    new_sl_at_new_sl_pnl_multiplier,
                    entryPrice,
                    trade_size,
                    leverage,
                    'long' if position['side'] == 'buy' else 'short'
                )

                pnl_threshold = trigger_pnl_multiplier * collateral

                if unrealized_pnl >= pnl_threshold:
                    old_sl_price = float(sl_order['price']) if sl_order else None

                    if position['side'] == 'buy':  # Long
                        new_sl_price = get_price_at_pnl(
                            pnl_multiplier=new_sl_pnl_multiplier,
                            order_fee=fee,
                            position_size_usd=collateral,
                            leverage=leverage,
                            entry_price=entryPrice,
                            type='long'
                        )
                        new_tp_price = get_price_at_pnl(
                            pnl_multiplier=leverage * 0.7,
                            order_fee=fee,
                            position_size_usd=collateral,
                            leverage=leverage,
                            entry_price=entryPrice,
                            type='long'
                        )
                        if old_sl_price is None or new_sl_price > old_sl_price:
                            print(f'{created_at} - TRIGGERED TRAILING STOP - {position.symbol} - NEW SL: ${new_sl_price:.3f}')
                            client.cancel_all_orders(trade_type='margin', src_currency=position['srcCurrency'], dst_currency=position['dstCurrency'])
                            oco = client.modify_sl_tp(position['id'], 'oco', position['liability'], new_tp_price, new_sl_price, new_sl_price)
                            print(oco)
                    else:  # Short
                        new_sl_price = get_price_at_pnl(
                            pnl_multiplier=new_sl_pnl_multiplier,
                            order_fee=fee,
                            position_size_usd=collateral,
                            leverage=leverage,
                            entry_price=entryPrice,
                            type='short'
                        )
                        new_sl_price = get_price_at_pnl(
                            pnl_multiplier=new_sl_pnl_multiplier,
                            order_fee=fee,
                            position_size_usd=collateral,
                            leverage=leverage,
                            entry_price=entryPrice,
                            type='short'
                        )
                        new_tp_price = get_price_at_pnl(
                            pnl_multiplier=leverage * 0.7,
                            order_fee=fee,
                            position_size_usd=collateral,
                            leverage=leverage,
                            entry_price=entryPrice,
                            type='short'
                        )

                        print(f'{created_at} - TRIGGERED TRAILING STOP - {symbol} - ENTRY_PRICE: {entryPrice} NEW SL: ${new_sl_price:.3f} - NEW TP: ${new_tp_price:.3f}')
                        if old_sl_price is None or new_sl_price < old_sl_price:
                            print(f'{created_at} - TRIGGERED TRAILING STOP - {symbol} - NEW SL: ${new_sl_price:.3f}')
                            client.cancel_all_orders(trade_type='margin', src_currency=position['srcCurrency'], dst_currency=position['dstCurrency'])
                            oco = client.modify_sl_tp(position['id'], 'oco', position['liability'], 2, new_sl_price, new_sl_price)
                            print(oco)
                    
                    break
            sleep(10)

def run_strategy_for_clients():
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(clients)) as executor:
        executor.map(run_strategy_for_client, clients)