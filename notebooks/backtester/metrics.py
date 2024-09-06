# metrics.py
import pandas as pd
import numpy as np

class Metrics:
    def calculate_metrics(self, trades_df, initial_capital):
        """
        Calculate performance metrics from trade data.
        
        :param trades_df: DataFrame containing trade data.
        :param initial_capital: Starting capital.
        :return: Dictionary of performance metrics.
        """
        total_profit = trades_df['pnl'].sum()
        num_trades = len(trades_df)
        win_rate = (trades_df['pnl'] > 0).mean()
        max_drawdown = self.calculate_max_drawdown(trades_df)
        sharpe_ratio = self.calculate_sharpe_ratio(trades_df)
        sortino_ratio = self.calculate_sortino_ratio(trades_df)
        
        performance_summary = {
            'Initial Capital': initial_capital,
            'Final Capital': trades_df['capital'].iloc[-1],
            'Maximum Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
            '# Trades': num_trades,
            'Win Rate': win_rate
        }
        return performance_summary

    def calculate_max_drawdown(self, trades_df):
        """
        Calculate the maximum drawdown.
        
        :param trades_df: DataFrame containing trade data.
        :return: Maximum drawdown.
        """
        capital = trades_df['capital']
        drawdowns = capital - capital.cummax()
        return drawdowns.min()

    def calculate_sharpe_ratio(self, trades_df, risk_free_rate=0.01):
        """
        Calculate the Sharpe ratio.
        
        :param trades_df: DataFrame containing trade data.
        :param risk_free_rate: The risk-free rate of return (default: 1%).
        :return: Sharpe ratio.
        """
        returns = trades_df['pnl'] / trades_df['capital'].shift(1)
        excess_returns = returns - risk_free_rate
        return excess_returns.mean() / returns.std() * np.sqrt(252)

    def calculate_sortino_ratio(self, trades_df, risk_free_rate=0.01):
        """
        Calculate the Sortino ratio.
        
        :param trades_df: DataFrame containing trade data.
        :param risk_free_rate: The risk-free rate of return (default: 1%).
        :return: Sortino ratio.
        """
        returns = trades_df['pnl'] / trades_df['capital'].shift(1)
        downside_returns = returns[returns < risk_free_rate]
        return returns.mean() / downside_returns.std() * np.sqrt(252)
