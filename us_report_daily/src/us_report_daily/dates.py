import datetime as dt
from dataclasses import dataclass

def yyyymmdd_to_date(s: str) -> dt.date:
    return dt.datetime.strptime(s, "%Y%m%d").date()

@dataclass(frozen=True)
class DatePack:
    asof: dt.date
    prev: dt.date
    mprev: dt.date
    ytd0: dt.date

def _nearest_le(dates: list[dt.date], target: dt.date) -> dt.date:
    c = [d for d in dates if d <= target]
    return max(c) if c else min(dates)

def build_date_pack(all_dates: list[dt.date], asof_str: str, gap: int) -> DatePack:
    asof = yyyymmdd_to_date(asof_str)
    dates = sorted(set(all_dates))
    if not dates:
        raise ValueError("no dates available from loaded series")

    t0 = _nearest_le(dates, asof)
    i = dates.index(t0)
    prev = dates[max(0, i - (gap + 1))]

    approx_mprev = t0 - dt.timedelta(days=30)
    mprev = _nearest_le(dates, approx_mprev)

    jan1 = dt.date(t0.year, 1, 1)
    ytd_candidates = [d for d in dates if jan1 <= d <= t0]
    ytd0 = ytd_candidates[0] if ytd_candidates else dates[0]

    return DatePack(asof=t0, prev=prev, mprev=mprev, ytd0=ytd0)