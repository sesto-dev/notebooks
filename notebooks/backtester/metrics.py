# metrics.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Metrics:
    def calculate_metrics(self, trades_df, initial_capital):
        total_profit = trades_df['pnl'].sum()
        num_trades = len(trades_df)
        win_rate = (trades_df['pnl'] > 0).mean()
        max_drawdown = trades_df['max_drawdown'].max()
        avg_drawdown = trades_df['max_drawdown'].mean()
        sharpe_ratio = trades_df['pnl'].mean() / trades_df['pnl'].std() * np.sqrt(252) if trades_df['pnl'].std() != 0 else 0
        
        performance_summary = {
            'Initial Capital': initial_capital,
            'Final Capital': trades_df['capital'].iloc[-1],
            'Maximum Capital': trades_df['capital'].max(),
            'Minimum Capital': trades_df['capital'].min(),
            'Volatility (Ann.)': trades_df['pnl'].std() * np.sqrt(252),
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Avg Drawdown': avg_drawdown,
            '# Trades': num_trades,
            'Win Rate': win_rate,
            'Best Trade': trades_df['pnl'].max(),
            'Worst Trade': trades_df['pnl'].min(),
            'Avg Trade': trades_df['pnl'].mean()
        }
        return performance_summary

    def plot_results(self, trades_df, initial_capital):
        trades_df['capital'] = initial_capital + trades_df['pnl'].cumsum()
        trades_df['capital'].plot(figsize=(10, 6))
        plt.title('Portfolio Capital Over Time')
        plt.xlabel('Trades')
        plt.ylabel('Capital')
        plt.grid(True)
        plt.show()
