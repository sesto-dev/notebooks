import numpy as np
import pandas as pd
from datetime import timedelta

def performance(trades_df, initial_capital):
    # Calculate Performance Metrics
    total_profit = trades_df['pnl'].sum()
    num_trades = len(trades_df)
    win_rate = (trades_df['pnl'] > 0).mean()
    max_drawdown = trades_df['max_drawdown'].min()
    avg_drawdown = trades_df['max_drawdown'].mean()
    best_trade = trades_df['pnl'].max()
    worst_trade = trades_df['pnl'].min()
    avg_trade = trades_df['pnl'].mean()
    trade_durations = (trades_df['close_time'] - trades_df['entry_time'])
    max_trade_duration = trade_durations.max()
    avg_trade_duration = trade_durations.mean()

    final_capital = initial_capital + total_profit
    max_capital = max(initial_capital, final_capital)
    min_capital = min(initial_capital, final_capital)

    # Annualized Volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio
    trading_days = 252
    total_days = (trades_df['close_time'].max() - trades_df['entry_time'].min()).days
    years = total_days / 365

    returns = trades_df['pnl'] / initial_capital
    total_return = (final_capital / initial_capital) - 1
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    
    daily_returns = returns.groupby(trades_df['close_time'].dt.date).sum()
    annualized_volatility = daily_returns.std() * np.sqrt(trading_days)
    
    risk_free_rate = 0.02  # Assume 2% risk-free rate
    excess_return = annualized_return - risk_free_rate
    sharpe_ratio = excess_return / annualized_volatility if annualized_volatility != 0 else 0
    
    downside_returns = daily_returns[daily_returns < 0]
    sortino_ratio = excess_return / (downside_returns.std() * np.sqrt(trading_days)) if len(downside_returns) > 0 else 0
    
    # Calculate drawdown
    cumulative_returns = (1 + trades_df['pnl'].cumsum() / initial_capital)
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    avg_drawdown = drawdown.mean()

    # Convert drawdown to dollar value
    max_drawdown_dollar = max_drawdown * initial_capital
    avg_drawdown_dollar = avg_drawdown * initial_capital

    # Calculate Calmar ratio
    calmar_ratio = abs(annualized_return / max_drawdown) if max_drawdown != 0 else 0

    # Additional metrics
    avg_profit = trades_df.loc[trades_df['pnl'] > 0, 'pnl'].mean()
    avg_loss = trades_df.loc[trades_df['pnl'] < 0, 'pnl'].mean()
    avg_risk_reward_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
    total_fees = trades_df['position_size_usd'].sum() * 0.0002  # Assuming 0.02% total fees (transaction cost + slippage)

    # New metrics
    first_trade_time = trades_df['entry_time'].min()
    last_trade_time = trades_df['close_time'].max()
    total_trading_days = (last_trade_time - first_trade_time).days
    avg_time_between_trades = (last_trade_time - first_trade_time) / num_trades if num_trades > 1 else timedelta(0)
    trades_per_day = num_trades / total_trading_days if total_trading_days > 0 else 0
    trades_per_week = trades_per_day * 7
    trades_per_month = trades_per_day * 30
    trades_per_year = trades_per_day * 365
    trades_left_open = (trades_df['closing_reason'] == 'end_of_backtest').sum()
    trades_closed_by_tp = (trades_df['closing_reason'] == 'tp').sum()
    trades_closed_by_sl = (trades_df['closing_reason'] == 'sl').sum()
    trades_closed_by_exit_condition = (trades_df['closing_reason'] == 'exit_condition').sum()

    # Summary Table with Proper Formatting
    performance_summary = pd.DataFrame({
        'Metric': ['Initial Capital', 'Final Capital', 'Total Profit', 'Return (%)', 'Annualized Return (%)',
                   'Volatility (Ann.)', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'Max. Drawdown ($)',
                   'Max. Drawdown (%)', 'Avg. Drawdown ($)', '# Trades', 'Win Rate', 'Best Trade ($)', 
                   'Worst Trade ($)', 'Avg. Trade ($)', 'Avg. Risk/Reward Ratio', 'Max. Trade Duration', 
                   'Avg. Trade Duration', 'Total Fees ($)', 'First Trade Time', 'Last Trade Time', 
                   'Avg. Time Between Trades', 'Trades per Day', 'Trades per Week', 'Trades per Month', 
                   'Trades per Year', 'Trades Left Open', 'Trades Closed by TP', 'Trades Closed by SL', 
                   'Trades Closed by Exit Condition'],
        'Value': [initial_capital, final_capital, total_profit, (final_capital / initial_capital - 1) * 100, annualized_return * 100,
                  annualized_volatility * 100, sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown_dollar,
                  max_drawdown * 100, avg_drawdown_dollar, num_trades, win_rate * 100, best_trade, 
                  worst_trade, avg_trade, avg_risk_reward_ratio, max_trade_duration, avg_trade_duration, 
                  total_fees, first_trade_time, last_trade_time, avg_time_between_trades, trades_per_day, 
                  trades_per_week, trades_per_month, trades_per_year, trades_left_open, trades_closed_by_tp, 
                  trades_closed_by_sl, trades_closed_by_exit_condition]
    })

    # Apply formatting to the 'Value' column
    performance_summary['Value'] = performance_summary.apply(lambda row: 
        f'{row["Value"]:.2f}' if isinstance(row["Value"], (int, float, np.integer, np.floating)) else str(row["Value"]), axis=1)

    # Add '%' symbol to percentage metrics
    percentage_metrics = ['Return (%)', 'Annualized Return (%)', 'Max. Drawdown (%)', 'Win Rate']
    performance_summary.loc[performance_summary['Metric'].isin(percentage_metrics), 'Value'] += '%'

    # Add '$' symbol to monetary metrics
    monetary_metrics = ['Initial Capital', 'Final Capital', 'Total Profit', 'Max. Drawdown ($)', 'Avg. Drawdown ($)',
                        'Best Trade ($)', 'Worst Trade ($)', 'Avg. Trade ($)', 'Total Fees ($)']
    performance_summary.loc[performance_summary['Metric'].isin(monetary_metrics), 'Value'] = '$' + performance_summary.loc[performance_summary['Metric'].isin(monetary_metrics), 'Value']

    return performance_summary