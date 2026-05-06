from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class SignalResult:
    score: int
    status: str
    trend: str
    volume: str
    risk: str
    summary: str
    action: str
    buy_zone: str
    stop_loss: str
    take_profit: str
    reasons: list[str]
    warnings: list[str]


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def analyze_stock(df: pd.DataFrame) -> SignalResult:
    if df.empty or len(df) < 60:
        raise ValueError("至少需要 60 个交易日数据才能分析")

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    close = _safe_float(latest["close"])
    ma5 = _safe_float(latest["ma5"])
    ma10 = _safe_float(latest["ma10"])
    ma20 = _safe_float(latest["ma20"])
    ma60 = _safe_float(latest["ma60"])
    rsi = _safe_float(latest["rsi14"])
    macd_hist = _safe_float(latest["macd_hist"])
    prev_macd_hist = _safe_float(prev["macd_hist"])
    vol_ratio = _safe_float(latest["vol_ratio"])
    pct_change = _safe_float(latest["pct_change"])

    if close is None:
        raise ValueError("缺少收盘价数据")

    score = 50
    reasons: list[str] = []
    warnings: list[str] = []

    # Trend score
    if ma5 and ma10 and ma20 and ma60:
        if close > ma5 > ma10 > ma20 > ma60:
            score += 25
            trend = "强趋势：价格位于多条均线上方，均线多头排列"
            reasons.append("股价站上 MA5/MA10/MA20/MA60，短中期趋势较强")
        elif close > ma20 and ma20 > ma60:
            score += 15
            trend = "趋势偏强：价格位于 20 日线之上，中期结构较好"
            reasons.append("股价站上 MA20，趋势尚未破坏")
        elif close < ma20:
            score -= 15
            trend = "趋势转弱：价格跌破 20 日线"
            warnings.append("股价跌破 MA20，需要警惕趋势走弱")
        else:
            trend = "震荡状态：均线结构尚不清晰"
    else:
        trend = "数据不足：均线结构无法完整判断"

    # Volume score
    if vol_ratio is not None:
        if vol_ratio >= 1.8 and pct_change and pct_change > 0:
            score += 15
            volume = "放量上涨：资金关注度明显提升"
            reasons.append("成交量明显高于 5 日均量，并伴随上涨")
        elif vol_ratio >= 1.8 and pct_change and pct_change < 0:
            score -= 15
            volume = "放量下跌：短线抛压较重"
            warnings.append("放量下跌，可能存在资金流出或情绪转弱")
        elif vol_ratio < 0.7:
            score -= 5
            volume = "缩量：资金参与度一般"
            warnings.append("当前量能不足，突破有效性需要观察")
        else:
            volume = "量能正常：成交量未出现极端变化"
    else:
        volume = "量能数据不足"

    # Momentum score
    if macd_hist is not None and prev_macd_hist is not None:
        if macd_hist > 0 and macd_hist > prev_macd_hist:
            score += 10
            reasons.append("MACD 柱体扩大，短线动能增强")
        elif macd_hist < 0 and macd_hist < prev_macd_hist:
            score -= 10
            warnings.append("MACD 负柱扩大，短线动能偏弱")

    if rsi is not None:
        if rsi >= 80:
            score -= 15
            warnings.append("RSI 高于 80，短线过热，追高风险较大")
        elif rsi >= 70:
            score -= 8
            warnings.append("RSI 高于 70，短线偏热")
        elif rsi <= 30:
            score -= 5
            warnings.append("RSI 低于 30，虽然超卖，但趋势可能仍弱")
        elif 45 <= rsi <= 65:
            score += 5
            reasons.append("RSI 处于相对健康区间，未明显过热")

    # Price location risk
    if pct_change is not None and pct_change >= 7:
        score -= 8
        warnings.append("单日涨幅较大，不建议情绪化追高")
    elif pct_change is not None and pct_change <= -5:
        score -= 8
        warnings.append("单日跌幅较大，需等待企稳信号")

    score = max(0, min(100, int(round(score))))

    if score >= 80:
        status = "强观察 / 可轻仓试错"
        action = "趋势和动能较好，但仍建议控制仓位，优先等待回踩确认，不建议满仓追高。"
        risk = "中"
    elif score >= 65:
        status = "观察 / 不追高"
        action = "可以加入重点观察池，等待回踩均线或突破确认后再考虑。"
        risk = "中"
    elif score >= 50:
        status = "持有为主"
        action = "如果已经持有，可继续观察趋势是否守住 MA20；如果未持有，不建议急于买入。"
        risk = "中等偏高"
    elif score >= 35:
        status = "减仓 / 谨慎"
        action = "趋势或量能存在问题，建议降低仓位，等待重新站回关键均线。"
        risk = "高"
    else:
        status = "止损 / 回避"
        action = "当前风险较高，建议回避或严格执行止损，等待新的趋势信号。"
        risk = "高"

    buy_zone = "等待回踩 MA5/MA10 或放量突破前高后观察"
    if ma5 and ma10:
        buy_zone = f"参考 MA5 {ma5:.2f} 与 MA10 {ma10:.2f} 附近的承接情况"

    stop_loss = "跌破 MA20 或亏损 5%-7% 时考虑止损"
    if ma20:
        stop_loss = f"重点观察 MA20 {ma20:.2f}，有效跌破则风险提升"

    take_profit = "短线可按 8%-15% 收益或前高压力位分批止盈"

    summary = f"综合评分 {score}/100，当前建议为：{status}。{trend}；{volume}。"

    if not reasons:
        reasons.append("暂未出现明显正向信号，建议继续观察")
    if not warnings:
        warnings.append("暂未发现极端风险，但仍需控制仓位和止损")

    return SignalResult(
        score=score,
        status=status,
        trend=trend,
        volume=volume,
        risk=risk,
        summary=summary,
        action=action,
        buy_zone=buy_zone,
        stop_loss=stop_loss,
        take_profit=take_profit,
        reasons=reasons,
        warnings=warnings,
    )
