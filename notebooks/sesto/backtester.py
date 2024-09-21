import pandas as pd
import numpy as np
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from sesto.performance import performance
from sesto.constants import MT5Timeframe
import time
from datetime import timedelta

@dataclass
class Trade:
    symbol: str
    entry_time: datetime
    entry_price: float
    position_type: str
    position_size_usd: float
    tp: float
    sl: float
    used_capital: float
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

    def __post_init__(self):
        self.calculate_potential_outcomes()

    def calculate_potential_outcomes(self):
        if self.position_type == 'long':
            self.potential_profit_usd = (self.tp - self.entry_price) * self.position_size_usd
            self.potential_loss_usd = (self.entry_price - self.sl) * self.position_size_usd
            self.tp_price_diff_percent = (self.tp - self.entry_price) / self.entry_price * 100
            self.sl_price_diff_percent = (self.entry_price - self.sl) / self.entry_price * 100
        else:  # short position
            self.potential_profit_usd = (self.entry_price - self.tp) * self.position_size_usd
            self.potential_loss_usd = (self.sl - self.entry_price) * self.position_size_usd
            self.tp_price_diff_percent = (self.entry_price - self.tp) / self.entry_price * 100
            self.sl_price_diff_percent = (self.sl - self.entry_price) / self.entry_price * 100

        # Calculate percentages based on used capital
        self.potential_profit_percent = (self.potential_profit_usd / self.used_capital) * 100
        self.potential_loss_percent = (self.potential_loss_usd / self.used_capital) * 100

class Backtester:
    def __init__(
        self, 
        data: Dict[MT5Timeframe, Dict[str, pd.DataFrame]], 
        initial_capital: float, 
        main_timeframe: MT5Timeframe,
        transaction_cost: float = 0.0001, 
        slippage: float = 0.0001,
        leverage: float = 500.0
    ):
        self.data = data
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.main_timeframe = main_timeframe
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.trade_log = []
        self.transaction_cost = transaction_cost
        self.slippage = slippage
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

    def calculate_position_size(self, capital_allocation: float, entry_price: float, symbol: str) -> float:
        # This is a simple position size calculation. You might want to adjust this based on your specific needs.
        return capital_allocation / entry_price

    def calculate_required_capital(self, entry_price: float, position_size_usd: float, symbol: str) -> float:
        # This calculates the required capital based on the leverage
        return (position_size_usd * entry_price) / self.leverage

    def open_trade(self, symbol: str, time: datetime, required_capital: float, position_size_usd: float, trade_info: Dict):
        trade = Trade(
            symbol=symbol,
            entry_time=time,
            entry_price=trade_info['entry_price'],
            position_type=trade_info['position_type'],
            position_size_usd=position_size_usd,
            tp=trade_info['tp'],
            sl=trade_info['sl'],
            used_capital=required_capital
        )
        self.open_trades.append(trade)
        self.available_capital -= required_capital
        print(f"Opened {trade.position_type} trade for {symbol} at {trade.entry_price}. Available capital: {self.available_capital:.2f}")

    def check_entry(self, symbol: str, time: datetime, row: pd.Series, timeframe: MT5Timeframe):
        trade_info = self.entry_condition(symbol, time, row, self.open_trades, self.closed_trades, timeframe)
        if trade_info:
            capital_allocation = trade_info['capital_allocation']
            position_size_usd = self.calculate_position_size(capital_allocation, trade_info['entry_price'], symbol)
            required_capital = self.calculate_required_capital(trade_info['entry_price'], position_size_usd, symbol)
            
            if required_capital <= self.available_capital:
                self.open_trade(symbol, time, required_capital, position_size_usd, trade_info)
            else:
                print(f"Not enough capital to open trade for {symbol} at {time}")

    def update_open_trades(self, symbol: str, time: datetime, row: pd.Series, timeframe: MT5Timeframe):
        for trade in self.open_trades[:]:
            if trade.symbol == symbol:
                self.update_trade_metrics(trade, row)
                
                if trade.position_type == 'long':
                    trade.unrealized_pnl = (row['close'] - trade.entry_price) / trade.entry_price * trade.position_size_usd
                else:  # short position
                    trade.unrealized_pnl = (trade.entry_price - row['close']) / trade.entry_price * trade.position_size_usd
                
                if self.exit_condition(trade, time, row, self.open_trades, self.closed_trades, timeframe):
                    self.close_trade(trade, time, row['close'], 'exit_condition')
                elif (trade.position_type == 'long' and row['close'] >= trade.tp) or (trade.position_type == 'short' and row['close'] <= trade.tp):
                    self.close_trade(trade, time, trade.tp, 'tp')
                elif (trade.position_type == 'long' and row['close'] <= trade.sl) or (trade.position_type == 'short' and row['close'] >= trade.sl):
                    self.close_trade(trade, time, trade.sl, 'sl')
                else:
                    self.trailing_stop(trade, time, row, self.open_trades, self.closed_trades, timeframe)

    def update_trade_metrics(self, trade: Trade, row: pd.Series):
        # Update max_drawdown and max_profit
        if trade.pnl is not None:
            trade.max_profit = max(trade.max_profit, trade.pnl)
            trade.max_drawdown = min(trade.max_drawdown, trade.pnl)

    def close_trade(self, trade: Trade, close_time: datetime, close_price: float, reason: str):
        trade.close_time = close_time
        trade.close_price = close_price
        trade.closing_reason = reason
        
        if trade.position_type == 'long':
            trade.pnl = (close_price - trade.entry_price) / trade.entry_price * trade.position_size_usd
        else:  # short position
            trade.pnl = (trade.entry_price - close_price) / trade.entry_price * trade.position_size_usd
        
        trade.pnl -= (trade.position_size_usd * self.transaction_cost) + (trade.position_size_usd * self.slippage)  # Account for closing costs
        
        trade.unrealized_pnl = 0
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.available_capital += trade.used_capital + trade.pnl
        self.trade_log.append(trade)

        print(f"Closed {trade.position_type} trade for {trade.symbol} at {close_price} with PNL {trade.pnl:.2f}. Available capital: {self.available_capital:.2f}")

    def close_all_trades(self, last_timestamp: datetime):
        for trade in self.open_trades[:]:  # Create a copy of the list to iterate over
            self.close_trade(trade, last_timestamp, self.data[self.main_timeframe][trade.symbol]['close'].iloc[-1], 'end_of_backtest')

    def generate_report(self):
        trades_df = pd.DataFrame([trade.__dict__ for trade in self.closed_trades])
        # timeframes that ac
        other_timeframes = [tf for tf in self.data.keys() if tf != self.main_timeframe]
        return performance(trades_df, self.initial_capital, self.main_timeframe, other_timeframes, self.backtest_duration)    

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