from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path
from typing import Any

_DEFAULT: dict[str, Any] = {
    "speakers": [],
    "summary": {"채권": "", "증시": "", "유가": "", "환시": ""},
    "indicators": [],
    # schedule keys can be dynamic, but keep a dict
    "schedule": {},
}

_WEEKDAY_EN = ["MON", "TUE", "WED", "THU", "FRI"]
_WEEKDAY_KR = ["월", "화", "수", "목", "금"]


def esc(s: str) -> str:
    """HTML-escape user text + keep line breaks."""
    return html.escape(s or "", quote=True).replace("\n", "<br>")


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def _write_default(p: Path) -> dict:
    _ensure_parent(p)
    p.write_text(json.dumps(_DEFAULT, ensure_ascii=False, indent=2), encoding="utf-8")
    # return a copy so callers can mutate safely
    return json.loads(json.dumps(_DEFAULT, ensure_ascii=False))


def load_content(path: str | Path) -> dict:
    """
    Load content JSON.
    Never raises due to missing/empty/broken JSON:
    - missing -> create default
    - empty   -> overwrite with default
    - broken  -> backup as .bad + overwrite with default
    Also patches missing keys to defaults.
    """
    p = Path(path)
    _ensure_parent(p)

    if not p.exists():
        return _write_default(p)

    raw = p.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return _write_default(p)

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            # weird but possible
            backup = p.with_suffix(p.suffix + ".bad")
            backup.write_text(raw, encoding="utf-8")
            return _write_default(p)

        # patch missing keys
        for k, v in _DEFAULT.items():
            if k not in data:
                data[k] = v

        # patch nested summary
        if not isinstance(data.get("summary"), dict):
            data["summary"] = dict(_DEFAULT["summary"])
        else:
            for k, v in _DEFAULT["summary"].items():
                if k not in data["summary"]:
                    data["summary"][k] = v

        # patch types
        if not isinstance(data.get("speakers"), list):
            data["speakers"] = []
        if not isinstance(data.get("indicators"), list):
            data["indicators"] = []
        if not isinstance(data.get("schedule"), dict):
            data["schedule"] = {}

        return data

    except Exception:
        # broken json => backup and recover
        backup = p.with_suffix(p.suffix + ".bad")
        backup.write_text(raw, encoding="utf-8")
        return _write_default(p)


def save_content(path: str | Path, content: dict) -> None:
    """Optional helper."""
    p = Path(path)
    _ensure_parent(p)
    p.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def render_speakers(speakers: list[dict]) -> str:
    """
    Returns HTML for speakers section.
    XSS-safe: all text escaped.
    """
    if not speakers:
        return '<div class="cm-item"><div class="cm-tx">—</div></div>'

    parts: list[str] = []
    for sp in speakers:
        name = esc(str(sp.get("name", "")))
        org = esc(str(sp.get("org", "")))
        text = esc(str(sp.get("text", "")))

        parts.append(
            '<div class="cm-item">'
            '<div class="cm-meta">'
            f'<span class="cm-name">{name}</span>'
            f'<span class="cm-org">{org}</span>'
            "</div>"
            f'<div class="cm-tx">{text}</div>'
            "</div>"
        )
    return "\n".join(parts)


def render_indicators(regions: list[dict]) -> str:
    """
    Returns HTML <tr> rows (tbody content).
    Expected shape:
      [{"region": "US", "items":[{"name":..,"actual":..,"survey":..,"prior":..}, ...]}, ...]
    """
    if not regions:
        return "<tr><td colspan='5' class='fl'>—</td></tr>"

    rows: list[str] = []
    for region in regions:
        label = esc(str(region.get("region", "")))
        rows.append(f"<tr class='rgn'><td colspan='5'>{label}</td></tr>")

        items = region.get("items", [])
        if not isinstance(items, list) or not items:
            rows.append("<tr><td colspan='5' class='fl'>—</td></tr>")
            continue

        for it in items:
            name = esc(str(it.get("name", "")))
            actual = esc(str(it.get("actual", "—")))
            survey = esc(str(it.get("survey", "—")))
            prior = esc(str(it.get("prior", "—")))
            rows.append(
                "<tr>"
                "<td></td>"
                f"<td>{name}</td>"
                f"<td class='v'>{actual}</td>"
                f"<td class='fl'>{survey}</td>"
                f"<td class='fl'>{prior}</td>"
                "</tr>"
            )
    return "\n".join(rows)


def _asof_week_mon(asof: dt.date) -> dt.date:
    """Monday of asof week."""
    return asof - dt.timedelta(days=asof.weekday())


def _md_key(d: dt.date) -> str:
    """'2/7' style (no leading zeros)."""
    return f"{d.month}/{d.day}"


def _week_keys(asof: dt.date) -> list[dt.date]:
    mon = _asof_week_mon(asof)
    return [mon + dt.timedelta(days=i) for i in range(5)]


def render_schedule(schedule: dict, asof_date: dt.date) -> str:
    """
    Returns HTML for schedule section.
    This version renders 5 columns (Mon~Fri) based on asof week.
    If your template expects different markup, adjust here.
    schedule dict key example: "2/17" -> list of events
    event: {"country":"US","event":"CPI","highlight":true}
    """
    days = _week_keys(asof_date)

    parts: list[str] = []
    for i, day in enumerate(days):
        key = _md_key(day)
        dw = _WEEKDAY_EN[i]
        events = schedule.get(key, [])
        if not isinstance(events, list):
            events = []

        entries: list[str] = []
        if events:
            for ev in events:
                country = esc(str(ev.get("country", "")))
                event = esc(str(ev.get("event", "")))
                hl = " hl" if bool(ev.get("highlight", False)) else ""
                entries.append(
                    "<div class='sched-entry'>"
                    f"<span class='sched-co'>{country}</span>"
                    f"<span class='sched-ev-nm{hl}'>{event}</span>"
                    "</div>"
                )
        else:
            entries.append(
                "<div class='sched-entry'>"
                "<span class='sched-co'></span>"
                "<span class='sched-ev-nm fl'>—</span>"
                "</div>"
            )

        parts.append(
            "<div class='sched-day-col'>"
            "<div class='sched-day-hd'>"
            f"<span class='sched-day-dt'>{esc(key)}</span>"
            f"<span class='sched-day-dw'>{esc(dw)}</span>"
            "</div>"
            + "\n".join(entries) +
            "</div>"
        )

    return "\n".join(parts)