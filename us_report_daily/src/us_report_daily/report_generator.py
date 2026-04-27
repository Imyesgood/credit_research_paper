import os
import math
import datetime as dt

from .mapping import REPORT_ITEM_CONFIG, SeriesSpec, BondSeriesSpec
from .excel_extract import open_book, load_series, load_bond_series, clear_cache
from .dates import build_date_pack, yyyymmdd_to_date
from .calc import compute_metrics_series, compute_metrics_bond
from .content_store import load_content, render_speakers, render_indicators, render_schedule, esc
from .template_renderer import render_template

def _is_nan(v) -> bool:
    try:
        return v is None or math.isnan(float(v))
    except Exception:
        return True

def fmt_t0(value, fmt: str) -> str:
    if _is_nan(value):
        return "—"
    v = float(value)
    return {
        "rate_kr":  f"{v:.2f}",
        "rate_us":  f"{v:.4f}",
        "rate_idx": f"{v:.3f}",
        "price":    f"{v:.3f}",
        "index":    f"{v:,.2f}",
        "fx":       f"{v:,.3f}",
    }.get(fmt, f"{v:.3f}")

def fmt_diff(value, diff_fmt: str) -> tuple[str, str]:
    if _is_nan(value):
        return "—", "fl"
    v = float(value)
    s = {
        "pct2":   f"{v:+.2f}%",
        "abs4":   f"{v:+.4f}",
        "abs2":   f"{v:+.2f}",
        "absbp2": f"{v:+.2f}",
        "absbp4": f"{v:+.4f}",
    }.get(diff_fmt, f"{v:+.4f}")
    cls = "p" if v > 0 else ("n" if v < 0 else "fl")
    return s, cls

def _weekday_kr(d: dt.date) -> str:
    names = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
    return names[d.weekday()]

def load_market_placeholders(book, asof_str: str, gap: int) -> tuple[dict[str, str], dict]:
    asof = yyyymmdd_to_date(asof_str)
    clear_cache()

    series_data = {}
    bond_data = {}
    errors = []

    # 1) load raw series
    for item, cfg in REPORT_ITEM_CONFIG.items():
        try:
            if cfg.is_bond:
                assert isinstance(cfg.spec, BondSeriesSpec)
                bond_data[item] = load_bond_series(book, cfg.spec.sheet, cfg.spec.block, asof)
            else:
                assert isinstance(cfg.spec, SeriesSpec)
                series_data[item] = load_series(book, cfg.spec.sheet, cfg.spec.block, cfg.spec.value_col, asof)
        except Exception as e:
            errors.append({"item": item, "error": str(e)})

    # 2) build datepack from union dates
    all_dates = sorted(
        {d for s in series_data.values() for d in s.index} |
        {d for bs in bond_data.values() for d in bs.today.index}
    )
    dp = build_date_pack(all_dates, asof_str, gap)

    # 3) compute metrics & placeholders
    out: dict[str, str] = {}
    for item, cfg in REPORT_ITEM_CONFIG.items():
        if cfg.is_bond and item in bond_data:
            m = compute_metrics_bond(bond_data[item], dp)
        elif (not cfg.is_bond) and item in series_data:
            m = compute_metrics_series(series_data[item], dp, cfg.use_diff)
        else:
            m = {"T0": None, "1D": None, "1M": None, "YTD": None}

        t0_str = fmt_t0(m["T0"], cfg.fmt)
        out[f"{item}|T0"] = t0_str
        out[f"CLS|{item}|T0"] = "v" if t0_str != "—" else "fl"

        for k in ["1D","1M","YTD"]:
            s, cls = fmt_diff(m[k], cfg.diff_fmt)
            out[f"{item}|{k}"] = s
            out[f"CLS|{item}|{k}"] = cls

    meta = {
        "asof": str(dp.asof),
        "prev": str(dp.prev),
        "mprev": str(dp.mprev),
        "ytd0": str(dp.ytd0),
        "errors": errors,
    }
    return out, meta

def generate_report(
    excel_path: str,
    asof_str: str,
    gap: int,
    content_path: str,
    template_path: str,
    output_path: str,
) -> str:
    book = open_book(excel_path)
    market, meta = load_market_placeholders(book, asof_str, gap)

    content = load_content(content_path)
    speakers_html = render_speakers(content.get("speakers", []))
    indicators_html = render_indicators(content.get("indicators", []))
    schedule_html = render_schedule(content.get("schedule", {}), yyyymmdd_to_date(asof_str))
    summary = content.get("summary", {})

    asof_date = yyyymmdd_to_date(asof_str)

    placeholders = {}
    placeholders.update(market)
    placeholders["REPORT_DATE"] = asof_date.strftime("%Y. %m. %d")
    placeholders["REPORT_WEEKDAY"] = _weekday_kr(asof_date)
    placeholders["SPEAKERS_HTML"] = speakers_html
    placeholders["INDICATORS_HTML"] = indicators_html
    placeholders["SCHEDULE_HTML"] = schedule_html
    placeholders["SUM_채권"] = esc(str(summary.get("채권","")))
    placeholders["SUM_증시"] = esc(str(summary.get("증시","")))
    placeholders["SUM_유가"] = esc(str(summary.get("유가","")))
    placeholders["SUM_환시"] = esc(str(summary.get("환시","")))

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    html = render_template(template_html, placeholders)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # 메타 로그 저장 (부분 실패해도 결과는 반드시 남김)
    meta_path = os.path.splitext(output_path)[0] + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        import json
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("[DATE]", meta["asof"], "prev=", meta["prev"], "mprev=", meta["mprev"], "ytd0=", meta["ytd0"])
    if meta["errors"]:
        print("[WARN] some items failed but report generated. see meta:", meta_path)

    return output_path