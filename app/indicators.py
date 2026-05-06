from __future__ import annotations

import numpy as np
import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators to OHLCV dataframe."""
    data = df.copy()
    close = data["close"]

    data["ma5"] = close.rolling(5).mean()
    data["ma10"] = close.rolling(10).mean()
    data["ma20"] = close.rolling(20).mean()
    data["ma60"] = close.rolling(60).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    data["rsi14"] = 100 - (100 / (1 + rs))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    data["macd_dif"] = ema12 - ema26
    data["macd_dea"] = data["macd_dif"].ewm(span=9, adjust=False).mean()
    data["macd_hist"] = (data["macd_dif"] - data["macd_dea"]) * 2

    data["vol_ma5"] = data["volume"].rolling(5).mean()
    data["vol_ratio"] = data["volume"] / data["vol_ma5"].replace(0, np.nan)

    data["pct_change"] = close.pct_change() * 100
    return data
