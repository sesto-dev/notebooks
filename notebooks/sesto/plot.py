import pandas as pd
from lightweight_charts import Chart
import plotly.express as px
from typing import List
from datetime import timedelta

# Type of Y is list of columns of df
def plot_plotly(df: pd.DataFrame, symbol: str, columns: List[str]):
    time_range = df['time'].max() - df['time'].min()
    
    # Define dynamic buttons based on the time range
    if time_range <= timedelta(hours=1):
        buttons = [
            dict(count=5, label="5m", step="minute", stepmode="backward"),
            dict(count=15, label="15m", step="minute", stepmode="backward"),
            dict(count=30, label="30m", step="minute", stepmode="backward"),
            dict(step="all")
        ]
    elif time_range <= timedelta(days=1):
        buttons = [
            dict(count=1, label="1h", step="hour", stepmode="backward"),
            dict(count=6, label="6h", step="hour", stepmode="backward"),
            dict(count=12, label="12h", step="hour", stepmode="backward"),
            dict(step="all")
        ]
    else:
        buttons = [
            dict(count=1, label="1d", step="day", stepmode="backward"),
            dict(count=7, label="1w", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(step="all")
        ]

    fig = px.line(df, x='time', y=columns, title=symbol, template="plotly_dark", render_mode="SVG")
    
    # Add range slider and selector with dynamic buttons
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=buttons,
                bgcolor='#323130',  # Dark background color
                activecolor='#515151',  # Slightly lighter color for active button
                font=dict(color='#E0E0E0')  # Light text color
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        # Center the range selector buttons
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.5,
            y=1.15,
            xanchor="center",
            yanchor="top"
        )]
    )
    
    fig.show()

def plot_tradingview(df: pd.DataFrame):
    chart = Chart(toolbox=True)
    chart.legend(True)
   
    chart.set(df)    
    chart.show(block=False)