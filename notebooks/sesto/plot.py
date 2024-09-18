import pandas as pd
from lightweight_charts import Chart
import plotly.express as px
from typing import List

# Type of Y is list of columns of df
def plot_plotly(df: pd.DataFrame, symbol: str, columns: List[str]):
    fig = px.line(df, x='time', y=columns, title=symbol, template="plotly_dark", render_mode="SVG")
    fig.show()

def plot_tradingview(df: pd.DataFrame):
    chart = Chart(toolbox=True)
    chart.legend(True)
   
    chart.set(df)    
    chart.show(block=False)