from adapters.data_layer import OHLCV
import pandas as pd
import numpy as np

def cal_rsi(ohlcvs: list[OHLCV], num_of_periods: int):
    # Convert list of OHLCV dicts to a DataFrame
    df = pd.DataFrame(ohlcvs)
    
    # Ensure sorted by timestamp
    df = df.sort_values("ts").reset_index(drop=True)
    
    # Calculate change in closing price
    delta = df["c"].diff()

    # Separate gains and losses
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # Create Series for rolling averages
    roll_up = pd.Series(gain).rolling(window=num_of_periods).mean()
    roll_down = pd.Series(loss).rolling(window=num_of_periods).mean()

    # Calculate RSI
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # Append RSI to DataFrame (optional)
    df["rsi"] = rsi

    return df  

def cal_ema(ohlcvs: list[OHLCV], num_of_periods: int):
    # Convert list of OHLCV dicts to a DataFrame
    df = pd.DataFrame(ohlcvs)
    
    # Ensure sorted by timestamp
    df = df.sort_values("ts").reset_index(drop=True)
    
    # Calculate EMA on closing price
    df["ema"] = df["c"].ewm(span=num_of_periods, adjust=False).mean()
    
    return df
    
def cal_rolling_twap(ohlcvs: list[OHLCV], window: int):
    df = pd.DataFrame(ohlcvs)
    df = df.sort_values("ts").reset_index(drop=True)

    df["twap"] = df["c"].rolling(window=window).mean()
    return df

def cal_rolling_vwap(ohlcvs: list[OHLCV], window: int):
    df = pd.DataFrame(ohlcvs)
    df = df.sort_values("ts").reset_index(drop=True)

    df["typical_price"] = (df["h"] + df["l"] + df["c"]) / 3
    df["tpv"] = df["typical_price"] * df["v"]  # typical price * volume

    df["vwap"] = (
        df["tpv"].rolling(window=window).sum() /
        df["v"].rolling(window=window).sum()
    )
    return df
