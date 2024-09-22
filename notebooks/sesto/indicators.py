import pandas as pd

def STD(df, period):
    df[f'std-{period}'] = df['close'].rolling(period).std()

def SMA(df, period):
    df[f'sma-{period}'] = df['close'].rolling(period).mean()

def EMA(df, period):
    df[f'ema-{period}'] = df['close'].ewm(span=period, adjust=False).mean()

def BB(df, period, std):
    rolling_mean = df['close'].rolling(period).mean()
    rolling_std = df['close'].rolling(period).std()

    df[f'bbm-{period}-{std}'] = rolling_mean
    df[f'bbu-{period}-{std}'] = rolling_mean + (rolling_std * std)
    df[f'bbl-{period}-{std}'] = rolling_mean - (rolling_std * std)

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

def ROC(df, period):
    df[f'roc-{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period) * 100

def MACD(df: pd.DataFrame, column: str = 'close', short_period: int = 12, long_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    ema_short = df[column].ewm(span=short_period, adjust=False).mean()
    ema_long = df[column].ewm(span=long_period, adjust=False).mean()
    df['macd'] = ema_short - ema_long
    df['macd-signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    df['macd-histogram'] = df['macd'] - df['macd-signal']

def ATR(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift(1)).abs()
    low_close = (df['low'] - df['close'].shift(1)).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = ranges.rolling(window=period).mean()
   
