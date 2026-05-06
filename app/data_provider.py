from __future__ import annotations

from datetime import datetime, timedelta

import akshare as ak
import pandas as pd


def normalize_symbol(symbol: str) -> str:
    code = symbol.strip().upper().replace("SH", "").replace("SZ", "")
    if not code.isdigit() or len(code) != 6:
        raise ValueError("请输入 6 位 A 股股票代码，例如 600519、000001、300750")
    return code


def fetch_a_share_daily(symbol: str, days: int = 180) -> pd.DataFrame:
    """Fetch A-share daily k-line data from AkShare.

    AkShare may change upstream fields over time. This function normalizes common Chinese columns
    into English fields used by the analysis engine.
    """
    code = normalize_symbol(symbol)
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")

    raw = ak.stock_zh_a_hist(
        symbol=code,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",
    )

    if raw is None or raw.empty:
        raise ValueError(f"未获取到 {code} 的行情数据")

    rename_map = {
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
        "振幅": "amplitude",
        "涨跌幅": "change_percent",
        "涨跌额": "change_amount",
        "换手率": "turnover",
    }
    data = raw.rename(columns=rename_map)
    required = ["date", "open", "close", "high", "low", "volume"]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(f"行情字段缺失：{missing}")

    data = data[required + [c for c in ["amount", "turnover"] if c in data.columns]].copy()
    data["date"] = pd.to_datetime(data["date"])
    for col in ["open", "close", "high", "low", "volume"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["close"]).sort_values("date").tail(days).reset_index(drop=True)
    return data
