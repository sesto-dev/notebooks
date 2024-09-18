import pandas as pd

def STD(df, period):
    df[f'std-{period}'] = df['close'].rolling(period).std()
    df.dropna(subset=[f'std-{period}'], inplace=True)

def SMA(df, period):
    df[f'sma-{period}'] = df['close'].rolling(period).mean()
    df.dropna(subset=[f'sma-{period}'], inplace=True)

def BB(df, period, std):
    rolling_mean = df['close'].rolling(period).mean()
    rolling_std = df['close'].rolling(period).std()

    df[f'bbm-{period}-{std}'] = rolling_mean
    df[f'bbu-{period}-{std}'] = rolling_mean + (rolling_std * std)
    df[f'bbl-{period}-{std}'] = rolling_mean - (rolling_std * std)

    df.dropna(subset=[f'bbm-{period}-{std}'], inplace=True)

def RSI(df: pd.DataFrame, period: int):   
    # Step 1: Calculate the price differences
    df['price_diff'] = df['close'].diff()

    # Step 2: Calculate gains and losses
    df['gain'] = df['price_diff'].apply(lambda x: x if x > 0 else 0)
    df['loss'] = df['price_diff'].apply(lambda x: -x if x < 0 else 0)
    
    # Step 3: Calculate the average gain and average loss using the smoothing period
    df['avg_gain'] = df['gain'].rolling(window=period, min_periods=period).mean()
    df['avg_loss'] = df['loss'].rolling(window=period, min_periods=period).mean()
    
    # Step 4: Calculate the Relative Strength (RS)
    df['rs'] = df['avg_gain'] / df['avg_loss']
    
    # Step 5: Calculate the RSI
    df[f'rsi-{period}'] = 100 - (100 / (1 + df['rs']))
    
    # Clean up intermediate columns
    df.drop(columns=['price_diff', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'], inplace=True)
    df.dropna(subset=[f'rsi-{period}'], inplace=True)