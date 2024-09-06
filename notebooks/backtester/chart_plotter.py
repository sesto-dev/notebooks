# chart_plotter.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class ChartPlotter:
    def __init__(self, trades_df, shared_data, indicators=None):
        """
        Initialize the ChartPlotter.
        
        :param trades_df: DataFrame containing trade information (entry/exit, prices, PnL, TP, SL, etc.).
        :param shared_data: Dictionary containing the price data (with time and close columns) for each symbol.
        :param indicators: Optional dictionary of indicators to plot (e.g., {'RSI': 'rsi'}).
        """
        self.trades_df = trades_df
        self.shared_data = shared_data
        self.indicators = indicators if indicators else {}

    def plot_trades_for_all_symbols(self):
        """
        Plot price and trade information for all symbols, along with optional indicators.
        """
        entry_color = '#2ca02c'  # Green for entry
        exit_color = '#d62728'   # Red for exit
        tp_color = '#1f77b4'     # Blue for Take Profit
        sl_color = '#ff7f0e'     # Orange for Stop Loss

        # Iterate through each symbol's data
        for symbol, price_data in self.shared_data.items():
            # Initialize the figure and GridSpec for the chart layout
            fig = plt.figure(figsize=(14, 10))
            gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])

            # Create the main price chart
            ax1 = plt.subplot(gs[0])
            ax1.plot(price_data['time'], price_data['close'], label=f'{symbol} Close Price', color='#1f77b4', linewidth=1.5)

            # Optional: Plot indicators on the second chart
            ax2 = plt.subplot(gs[1]) if self.indicators else None
            self._plot_indicators(symbol, price_data, ax2)

            # Filter trades for the current symbol
            symbol_trades = self.trades_df[self.trades_df['symbol'] == symbol].copy()
            symbol_trades['entry_time'] = pd.to_datetime(symbol_trades['entry_time'])
            symbol_trades['exit_time'] = pd.to_datetime(symbol_trades['exit_time'])

            # Plot trades on the price chart
            self._plot_trades(ax1, symbol_trades, entry_color, exit_color, tp_color, sl_color)

            # Formatting the price chart
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Price')
            ax1.set_title(f'{symbol} Price Chart and Trades')
            ax1.legend(loc='upper left')
            ax1.grid(True)

            # If indicators were plotted, format the second chart
            if ax2:
                ax2.set_xlabel('Date')
                ax2.grid(True)

            # Adjust the layout for better appearance
            plt.tight_layout()
            plt.show()

    def _plot_indicators(self, symbol, price_data, ax2):
        """
        Plot the indicators (if any) on the second chart.
        
        :param symbol: The symbol for which the indicators are being plotted.
        :param price_data: The price data for the symbol.
        :param ax2: The axes object for the second subplot (for indicators).
        """
        if not ax2 or not self.indicators:
            return

        for indicator_name, column_name in self.indicators.items():
            if column_name in price_data.columns:
                ax2.plot(price_data['time'], price_data[column_name], label=indicator_name, linestyle='--', linewidth=1.5)

        ax2.set_ylabel(', '.join(self.indicators.keys()))
        ax2.legend(loc='upper left')

    def _plot_trades(self, ax1, symbol_trades, entry_color, exit_color, tp_color, sl_color):
        """
        Plot the trades on the price chart.
        
        :param ax1: The axes object for the price chart.
        :param symbol_trades: DataFrame containing trade data for the specific symbol.
        :param entry_color: Color for the entry points.
        :param exit_color: Color for the exit points.
        :param tp_color: Color for the Take Profit lines.
        :param sl_color: Color for the Stop Loss lines.
        """
        for i, trade in symbol_trades.iterrows():
            entry_time = trade['entry_time']
            exit_time = trade['exit_time']
            entry_price = trade['entry_price']
            tp = trade['tp']
            sl = trade['sl']
            close_price = trade['close_price']
            pnl = trade['pnl']

            # Plot the trade entry and exit
            ax1.plot([entry_time, exit_time], [entry_price, close_price], marker='o',
                     color=entry_color if pnl > 0 else exit_color, linestyle='-', linewidth=2)

            # Plot TP and SL as horizontal lines
            ax1.hlines(tp, xmin=entry_time, xmax=exit_time, colors=tp_color, linestyles='dotted', linewidth=1.5)
            ax1.hlines(sl, xmin=entry_time, xmax=exit_time, colors=sl_color, linestyles='dotted', linewidth=1.5)

            # Annotate the trade with PnL
            ax1.annotate(f'PnL: {pnl:.2f}', (exit_time, close_price), textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=8, color='black')
