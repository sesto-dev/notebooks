import pandas as pd
import numpy as np
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from sesto.performance import performance

@dataclass
class Trade:
    symbol: str
    entry_time: datetime
    entry_price: float
    position_type: str
    volume: float
    tp: float
    sl: float
    used_capital: float
    close_time: datetime = None
    close_price: float = None
    pnl: float = None
    max_drawdown: float = 0
    max_profit: float = 0
    closing_reason: str = None
    unrealized_pnl: float = 0

class Backtester:
    def __init__(
        self, 
        data: Dict[str, pd.DataFrame], 
        initial_capital: float, 
        transaction_cost: float = 0.0001, 
        slippage: float = 0.0001,
        leverage: float = 500.0  # Added leverage parameter
    ):
        self.data = data
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.trade_log = []
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.leverage = leverage  # Initialize leverage

    def run(self):
        for symbol, df in self.data.items():
            for _, row in df.iterrows():
                self.update_open_trades(symbol, row['time'], row)
                self.check_entry(symbol, row['time'], row)
        
        self.close_all_trades(list(self.data.values())[-1]['time'].iloc[-1])

    def check_entry(self, symbol: str, time: datetime, row: pd.Series):
        trade_info = self.entry_condition(symbol, time, row, self.open_trades, self.closed_trades)
        if trade_info:
            required_capital = self.calculate_required_capital(trade_info['entry_price'], trade_info['volume'], symbol)
            if required_capital <= self.available_capital:
                self.open_trade(symbol, time, required_capital, **trade_info)
            else:
                print(f"Not enough capital to open trade for {symbol} at {time}")

    def calculate_required_capital(self, entry_price: float, volume: float, symbol: str) -> float:
        notional_value = entry_price * volume
        margin_required = notional_value / self.leverage  # Adjust for leverage
        transaction_cost = notional_value * self.transaction_cost
        slippage_cost = notional_value * self.slippage
        return margin_required + transaction_cost + slippage_cost  # Use margin as used capital

    def open_trade(self, symbol: str, entry_time: datetime, required_capital: float, entry_price: float, position_type: str, volume: float, tp: float, sl: float):
        trade = Trade(
            symbol=symbol,
            entry_time=entry_time,
            entry_price=entry_price,
            position_type=position_type,
            volume=volume,
            tp=tp,
            sl=sl,
            used_capital=required_capital
        )
        self.open_trades.append(trade)
        self.available_capital -= required_capital
        print(f"Opened {position_type} trade for {symbol} at {entry_price}. Available capital: {self.available_capital:.2f}")

    def update_open_trades(self, symbol: str, time: datetime, row: pd.Series):
        for trade in self.open_trades[:]:  # Create a copy of the list to iterate over
            if trade.symbol == symbol:
                self.update_trade_metrics(trade, row)
                
                # Update unrealized_pnl with leverage
                if trade.position_type == 'long':
                    trade.unrealized_pnl = (row['close'] - trade.entry_price) * trade.volume * self.leverage
                else:  # short position
                    trade.unrealized_pnl = (trade.entry_price - row['close']) * trade.volume * self.leverage
                
                if self.exit_condition(trade, time, row, self.open_trades, self.closed_trades):
                    self.close_trade(trade, time, row['close'], 'exit_condition')
                elif (trade.position_type == 'long' and row['close'] >= trade.tp) or (trade.position_type == 'short' and row['close'] <= trade.tp):
                    self.close_trade(trade, time, trade.tp, 'tp')
                elif (trade.position_type == 'long' and row['close'] <= trade.sl) or (trade.position_type == 'short' and row['close'] >= trade.sl):
                    self.close_trade(trade, time, trade.sl, 'sl')
                else:
                    self.trailing_stop(trade, time, row, self.open_trades, self.closed_trades)

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
            trade.pnl = (close_price - trade.entry_price) * trade.volume * self.leverage
        else:  # short position
            trade.pnl = (trade.entry_price - close_price) * trade.volume * self.leverage
        
        trade.pnl -= (close_price * trade.volume * self.transaction_cost) + (close_price * trade.volume * self.slippage)  # Account for closing costs
        
        trade.unrealized_pnl = 0
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.available_capital += trade.used_capital + trade.pnl
        self.trade_log.append(trade)

        print(f"Closed {trade.position_type} trade for {trade.symbol} at {close_price} with PNL {trade.pnl:.4f}. Available capital: {self.available_capital:.2f}")

    def close_all_trades(self, last_timestamp: datetime):
        for trade in self.open_trades[:]:  # Create a copy of the list to iterate over
            self.close_trade(trade, last_timestamp, self.data[trade.symbol]['close'].iloc[-1], 'end_of_backtest')

    def generate_report(self):
        trades_df = pd.DataFrame([trade.__dict__ for trade in self.closed_trades])
        return performance(trades_df, self.initial_capital)
    
    def entry_condition(self, symbol: str, time: datetime, row: pd.Series, open_trades: List[Trade], closed_trades: List[Trade]) -> Optional[Dict]:
        # This method should be overridden in the subclass
        return None

    def exit_condition(self, trade: Trade, time: datetime, row: pd.Series, open_trades: List[Trade], closed_trades: List[Trade]) -> bool:
        # This method should be overridden in the subclass
        return False

    def trailing_stop(self, trade: Trade, time: datetime, row: pd.Series, open_trades: List[Trade], closed_trades: List[Trade]):
        # This method should be overridden in the subclass
        pass