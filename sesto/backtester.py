import pandas as pd
import numpy as np
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from sesto.performance import performance
from sesto.constants import MT5Timeframe
from sesto.utils import calculate_position_size, get_price_at_pnl, calculate_fee, calculate_break_even_price, calculate_price_with_spread, calculate_liquidation_price
import time
from datetime import timedelta

@dataclass
class Trade:
    symbol: str
    entry_time: datetime
    entry_p: float
    type: str
    position_size_usd: float
    tp_p: float
    sl_p: float
    capital: float
    potential_profit_usd: float = field(init=False)
    potential_profit_percent: float = field(init=False)
    potential_loss_usd: float = field(init=False)
    potential_loss_percent: float = field(init=False)
    tp_price_diff_percent: float = field(init=False)
    sl_price_diff_percent: float = field(init=False)
    close_time: datetime = None
    close_price: float = None
    pnl: float = None
    max_drawdown: float = 0
    max_profit: float = 0
    closing_reason: str = None
    unrealized_pnl: float = 0
    leverage: float = 500.0
    liq_p: float = None
    be_p: float = None
    order_fee: float = None
    spread_multiplier: float = 0.0001
    fee_multiplier: float = 0.0001

    def __post_init__(self):
        if self.type == 'long':
            self.entry_p = calculate_price_with_spread(self.entry_p, self.spread_multiplier, increase=True)
            self.tp_p = calculate_price_with_spread(self.tp_p, self.spread_multiplier, increase=False)    
            self.sl_p = calculate_price_with_spread(self.sl_p, self.spread_multiplier, increase=True)
        else:
            self.entry_p = calculate_price_with_spread(self.entry_p, self.spread_multiplier, increase=False)
            self.tp_p = calculate_price_with_spread(self.tp_p, self.spread_multiplier, increase=True)
            self.sl_p = calculate_price_with_spread(self.sl_p, self.spread_multiplier, increase=False)

        self.order_fee = calculate_fee(self.position_size_usd)
        self.be_p = calculate_break_even_price(self.entry_p, self.order_fee, self.position_size_usd, self.type)
        self.calculate_potential_outcomes()
        
        self.liq_p = calculate_liquidation_price(entry_price=self.entry_p, leverage=self.leverage, type=self.type)    

    def calculate_potential_outcomes(self):
        if self.type == 'long':            
            self.potential_profit_usd = ((self.tp_p - self.entry_p ) / self.entry_p * self.position_size_usd) - self.order_fee
            self.potential_loss_usd = ((self.entry_p - self.sl_p) / self.entry_p * self.position_size_usd) - self.order_fee
            self.tp_price_diff_percent = (self.potential_profit_usd / self.capital) * 100
            self.sl_price_diff_percent = (self.potential_loss_usd / self.capital) * 100
        else:  # short position            
            self.potential_profit_usd = ((self.entry_p - self.tp_p) / self.entry_p * self.position_size_usd) - self.order_fee
            self.potential_loss_usd = ((self.sl_p - self.entry_p) / self.entry_p * self.position_size_usd) - self.order_fee
            self.tp_price_diff_percent = (self.potential_profit_usd / self.capital) * 100
            self.sl_price_diff_percent = (self.potential_loss_usd / self.capital) * 100

        # Calculate percentages based on used capital
        self.potential_profit_percent = (self.potential_profit_usd / self.capital) * 100
        self.potential_loss_percent = (self.potential_loss_usd / self.capital) * 100

class Backtester:
    def __init__(
        self, 
        data: Dict[MT5Timeframe, Dict[str, pd.DataFrame]], 
        initial_capital: float, 
        main_timeframe: MT5Timeframe,
        fee_multiplier: float = 0.0001,
        spread_multiplier: float = 0.0001,
        leverage: float = 500.0
    ):
        self.data = data
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.main_timeframe = main_timeframe
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.trade_log = []
        self.fee_multiplier = fee_multiplier
        self.spread_multiplier = spread_multiplier
        self.leverage = leverage
        self.backtest_duration = None

    def run(self):
        start_time = time.time()

        if self.main_timeframe not in self.data:
            raise ValueError(f"Main timeframe {self.main_timeframe} not found in data")

        for symbol, df in self.data[self.main_timeframe].items():
            for _, row in df.iterrows():
                self.update_open_trades(symbol, row['time'], row, self.main_timeframe)
                self.check_entry(symbol, row['time'], row, self.main_timeframe)
        
        self.close_all_trades(list(self.data[self.main_timeframe].values())[-1]['time'].iloc[-1])
        
        end_time = time.time()
        self.backtest_duration = timedelta(seconds=end_time - start_time)

    def open_trade(self, symbol: str, time: datetime, required_capital: float, position_size_usd: float, trade_info: Dict):
        trade = Trade(
            symbol=symbol,
            entry_time=time,
            entry_p=trade_info['entry_p'],
            type=trade_info['type'],
            position_size_usd=position_size_usd,
            tp_p=trade_info['tp_p'],
            sl_p=trade_info['sl_p'],
            capital=required_capital,
            leverage=self.leverage,
            spread_multiplier=self.spread_multiplier,
            fee_multiplier=self.fee_multiplier
        )

        self.open_trades.append(trade)
        self.available_capital -= required_capital + trade.order_fee
        print(f"{time} - {symbol} - OPENED TRADE - {trade.type} - ENTRY: ${trade.entry_p:.3f} - TP: ${trade.tp_p:.3f} - SL: ${trade.sl_p:.3f} - LIQ: ${trade.liq_p:.3f} - BE: ${trade.be_p:.3f} - AVAILABLE CAPITAL: ${self.available_capital:.3f}")

    def check_entry(self, symbol: str, time: datetime, row: pd.Series, timeframe: MT5Timeframe):
        trade_info = self.entry_condition(symbol, time, row, self.open_trades, self.closed_trades, timeframe)
        if trade_info:
            capital = trade_info['capital']
            position_size_usd = calculate_position_size(capital, self.leverage)
            
            if capital <= self.available_capital:
                self.open_trade(symbol, time, capital, position_size_usd, trade_info)
            else:
                print(f"Not enough capital to open trade for {symbol} at {time}")

    def update_open_trades(self, symbol: str, time: datetime, row: pd.Series, timeframe: MT5Timeframe):
        for trade in self.open_trades[:]:
            if trade.symbol == symbol:
                self.update_trade_metrics(trade, row)

                long_trade_should_close_at_tp = trade.type == 'long' and (row['close'] >= trade.tp_p)
                short_trade_should_close_at_tp = trade.type == 'short' and (row['close'] <= trade.tp_p)
                long_trade_should_close_at_sl = trade.type == 'long' and (row['close'] <= trade.sl_p)
                short_trade_should_close_at_sl = trade.type == 'short' and (row['close'] >= trade.sl_p)
                long_trade_should_liquidate = trade.type == 'long' and (row['close'] <= trade.liq_p or trade.unrealized_pnl < (trade.capital * -0.99) )
                short_trade_should_liquidate = trade.type == 'short' and (row['close'] >= trade.liq_p or trade.unrealized_pnl < (trade.capital * -0.99) )
                
                if self.exit_condition(trade, time, row, self.open_trades, self.closed_trades, timeframe):
                    self.close_trade(trade, time, row['close'], 'exit_condition')
                elif long_trade_should_close_at_tp or short_trade_should_close_at_tp:
                    self.close_trade(trade, time, trade.tp_p, 'TP')
                elif long_trade_should_liquidate or short_trade_should_liquidate:
                    self.close_trade(trade, time, trade.sl_p, 'LIQ')
                elif long_trade_should_close_at_sl or short_trade_should_close_at_sl:
                    self.close_trade(trade, time, trade.sl_p, 'SL')
                else:
                    self.trailing_stop(trade, time, row, self.open_trades, self.closed_trades, timeframe)

    def update_trade_metrics(self, trade: Trade, row: pd.Series):
        if trade.type == 'long':
            trade.unrealized_pnl = ((row['close'] - trade.entry_p) / trade.entry_p * trade.position_size_usd) - trade.order_fee
        else:  # short position
            trade.unrealized_pnl = ((trade.entry_p - row['close']) / trade.entry_p * trade.position_size_usd) - trade.order_fee

        # Update max_drawdown and max_profit
        if trade.pnl is not None:
            trade.max_profit = max(trade.max_profit, trade.unrealized_pnl)
            trade.max_drawdown = min(trade.max_drawdown, trade.unrealized_pnl)

    def close_trade(self, trade: Trade, close_time: datetime, close_price: float, reason: str):
        trade.close_time = close_time
        trade.closing_reason = reason
        
        if trade.type == 'long':
            trade.close_price = close_price * (1 - self.spread_multiplier)
            trade.pnl = ((trade.close_price - trade.entry_p) / trade.entry_p * trade.position_size_usd) - trade.order_fee
        else:  # short position
            trade.close_price = close_price * (1 + self.spread_multiplier)
            trade.pnl = ((trade.entry_p - trade.close_price) / trade.entry_p * trade.position_size_usd) - trade.order_fee
                
        trade.unrealized_pnl = 0
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.available_capital += trade.capital + trade.pnl
        self.trade_log.append(trade)

        print(f"{trade.close_time} - {trade.symbol} - CLOSED TRADE - {trade.type} - ENTRY: ${trade.entry_p:.3f} - CLOSE: ${close_price:.3f} - PNL: ${trade.pnl:.2f} - SL: ${trade.sl_p:.3f} - TP: ${trade.tp_p:.3f} - REASON: {reason} - AVAILABLE CAPITAL: ${self.available_capital:.3f}")

    def close_all_trades(self, last_timestamp: datetime):
        for trade in self.open_trades[:]:  # Create a copy of the list to iterate over
            self.close_trade(trade, last_timestamp, self.data[self.main_timeframe][trade.symbol]['close'].iloc[-1], 'end_of_backtest')

    def generate_report(self):
        trades_df = pd.DataFrame([trade.__dict__ for trade in self.closed_trades])

        return performance(trades_df, self.initial_capital, self.main_timeframe, self.backtest_duration)    

    def generate_report_per_symbol(self):
        symbol_reports = {}
        for symbol in self.data.keys():
            symbol_trades = [trade for trade in self.closed_trades if trade.symbol == symbol]
            if symbol_trades:
                trades_df = pd.DataFrame([trade.__dict__ for trade in symbol_trades])
                report = performance(trades_df, self.initial_capital)
                
                # Insert a row at the top with the symbol
                symbol_row = pd.DataFrame({'Metric': ['Symbol'], 'Value': [symbol]})
                report = pd.concat([symbol_row, report]).reset_index(drop=True)
                
                symbol_reports[symbol] = report
            else:
                print(f"No closed trades for symbol: {symbol}")
        return symbol_reports
    
    def entry_condition(self, symbol: str, time: datetime, row: pd.Series, open_trades: List[Trade], closed_trades: List[Trade]) -> Optional[Dict]:
        # This method should be overridden in the subclass
        return None

    def exit_condition(self, trade: Trade, time: datetime, row: pd.Series, open_trades: List[Trade], closed_trades: List[Trade]) -> bool:
        # This method should be overridden in the subclass
        return False

    def trailing_stop(self, trade: Trade, time: datetime, row: pd.Series, open_trades: List[Trade], closed_trades: List[Trade]):
        # This method should be overridden in the subclass
        pass