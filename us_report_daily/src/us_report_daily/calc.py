import math
import pandas as pd
from .dates import DatePack

def _nearest_value(s: pd.Series, d) -> float:
    c = s[s.index <= d]
    return float(c.iloc[-1]) if not c.empty else float("nan")

def compute_metrics_series(s: pd.Series, dp: DatePack, use_diff: bool) -> dict[str, float]:
    t0 = _nearest_value(s, dp.asof)
    p1 = _nearest_value(s, dp.prev)
    pm = _nearest_value(s, dp.mprev)
    y0 = _nearest_value(s, dp.ytd0)

    def pct(a, b):
        if any(map(lambda x: x is None or math.isnan(x), [a, b])) or b == 0:
            return float("nan")
        return (a / b - 1.0) * 100.0

    def diff(a, b):
        if any(map(lambda x: x is None or math.isnan(x), [a, b])):
            return float("nan")
        return a - b

    if use_diff:
        return {"T0": t0, "1D": diff(t0, p1), "1M": diff(t0, pm), "YTD": diff(t0, y0)}
    return {"T0": t0, "1D": pct(t0, p1), "1M": pct(t0, pm), "YTD": pct(t0, y0)}

def compute_metrics_bond(bs, dp: DatePack) -> dict[str, float]:
    t0 = bs.value(dp.asof)
    p1 = bs.value_prev(dp.asof)
    pm = bs.value(dp.mprev)
    y0 = bs.value(dp.ytd0)

    def diff_bp(a, b):
        if any(map(lambda x: x is None or math.isnan(x), [a, b])):
            return float("nan")
        return (a - b) * 100.0  # bp

    return {"T0": t0, "1D": diff_bp(t0, p1), "1M": diff_bp(t0, pm), "YTD": diff_bp(t0, y0)}