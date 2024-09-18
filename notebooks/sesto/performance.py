import numpy as np
import pandas as pd

def performance(trades_df, initial_capital):
    # Calculate Performance Metrics
    total_profit = trades_df['pnl'].sum()
    num_trades = len(trades_df)
    win_rate = (trades_df['pnl'] > 0).mean()
    max_drawdown = trades_df['max_drawdown'].max()
    avg_drawdown = trades_df['max_drawdown'].mean()
    best_trade = trades_df['pnl'].max()
    worst_trade = trades_df['pnl'].min()
    avg_trade = trades_df['pnl'].mean()
    trade_durations = (trades_df['exit_time'] - trades_df['entry_time'])
    max_trade_duration = trade_durations.max()
    avg_trade_duration = trade_durations.mean()
    profit_factor = trades_df.loc[trades_df['pnl'] > 0, 'pnl'].sum() / -trades_df.loc[trades_df['pnl'] < 0, 'pnl'].sum()

    final_capital = trades_df['capital'].iloc[-1]
    max_capital = trades_df['capital'].max()
    min_capital = trades_df['capital'].min()

    # Annualized Volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio
    trading_days = 252
    annualized_volatility = trades_df['pnl'].std() * np.sqrt(trading_days)
    sharpe_ratio = trades_df['pnl'].mean() / trades_df['pnl'].std() * np.sqrt(trading_days)
    sortino_ratio = trades_df['pnl'].mean() / trades_df[trades_df['pnl'] < 0]['pnl'].std() * np.sqrt(trading_days)
    calmar_ratio = trades_df['pnl'].sum() / max_drawdown

    # Summary Table with Proper Formatting
    performance_summary = pd.DataFrame({
        'Metric': ['Initial Capital', 'Final Capital', 'Maximum Capital', 'Minimum Capital', 
                'Volatility (Ann.)', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'Max. Drawdown',
                'Avg. Drawdown', '# Trades', 'Win Rate', 'Best Trade', 'Worst Trade', 'Avg. Trade',
                'Max. Trade Duration', 'Avg. Trade Duration', 'Profit Factor'],
        'Value': [initial_capital, final_capital, max_capital, min_capital,
                annualized_volatility, sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown,
                avg_drawdown, num_trades, win_rate, best_trade, worst_trade, avg_trade,
                max_trade_duration, avg_trade_duration, profit_factor]
    })

    # Apply formatting to the 'Value' column
    performance_summary['Value'] = performance_summary['Value'].apply(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)

    return performance_summary