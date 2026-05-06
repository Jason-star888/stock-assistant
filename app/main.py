from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import analyze_stock
from app.data_provider import fetch_a_share_daily, normalize_symbol
from app.indicators import add_indicators

app = FastAPI(title="AI Stock Assistant MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "AI Stock Assistant MVP",
        "usage": "GET /analyze?symbol=600519",
        "disclaimer": "仅用于个人研究和交易辅助，不构成投资建议。",
    }


@app.get("/analyze")
def analyze(symbol: str = Query(..., description="6 位 A 股代码，例如 600519")):
    code = normalize_symbol(symbol)
    daily = fetch_a_share_daily(code)
    enriched = add_indicators(daily)
    result = analyze_stock(enriched)

    latest = enriched.iloc[-1]
    recent = enriched.tail(30)

    return {
        "symbol": code,
        "date": str(latest["date"].date()),
        "latest": {
            "close": round(float(latest["close"]), 2),
            "pct_change": None if latest["pct_change"] != latest["pct_change"] else round(float(latest["pct_change"]), 2),
            "ma5": round(float(latest["ma5"]), 2),
            "ma10": round(float(latest["ma10"]), 2),
            "ma20": round(float(latest["ma20"]), 2),
            "ma60": round(float(latest["ma60"]), 2),
            "rsi14": None if latest["rsi14"] != latest["rsi14"] else round(float(latest["rsi14"]), 2),
            "macd_hist": round(float(latest["macd_hist"]), 4),
            "vol_ratio": None if latest["vol_ratio"] != latest["vol_ratio"] else round(float(latest["vol_ratio"]), 2),
        },
        "analysis": result.__dict__,
        "chart": [
            {
                "date": str(row["date"].date()),
                "close": round(float(row["close"]), 2),
                "ma5": None if row["ma5"] != row["ma5"] else round(float(row["ma5"]), 2),
                "ma20": None if row["ma20"] != row["ma20"] else round(float(row["ma20"]), 2),
                "volume": int(row["volume"]),
            }
            for _, row in recent.iterrows()
        ],
    }
