import os
import sys
import datetime as dt
import webbrowser
from pathlib import Path

# ----- 0) robust paths: project root fixed -----
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from us_report_daily.report_generator import generate_report  # noqa

# ----- 1) defaults: one-click run -----
EXCEL_PATH = BASE_DIR / "US_data.xlsx"
CONTENT_PATH = BASE_DIR / "content" / "content.json"
TEMPLATE_PATH = BASE_DIR / "template.html"
OUTPUT_DIR = BASE_DIR / "output"

# 날짜 자동: 오늘(로컬) 기준. 엑셀 최신일을 자동 탐지하려면 다음 단계에서 붙일 수 있음.
ASOF = dt.date.today().strftime("%Y%m%d")
GAP = 0


def _ensure_dirs():
    (BASE_DIR / "content").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "templates").mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_template():
    if TEMPLATE_PATH.exists():
        return
    TEMPLATE_PATH.write_text(
        """<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>Report</title></head>
<body>
  <h1>{{REPORT_DATE}} ({{REPORT_WEEKDAY}})</h1>
  <h2>Market</h2>
  <div>USD/KRW: {{USD/KRW|T0}} / {{USD/KRW|1D}} / {{USD/KRW|1M}} / {{USD/KRW|YTD}}</div>
  <div>S&P500: {{S&P500|T0}} / {{S&P500|1D}} / {{S&P500|1M}} / {{S&P500|YTD}}</div>
  <div>WTI: {{WTI|T0}} / {{WTI|1D}} / {{WTI|1M}} / {{WTI|YTD}}</div>

  <h2>Summary</h2>
  <div>채권: {{SUM_채권}}</div>
  <div>증시: {{SUM_증시}}</div>
  <div>유가: {{SUM_유가}}</div>
  <div>환시: {{SUM_환시}}</div>

  <h2>Speakers</h2>
  {{SPEAKERS_HTML}}

  <h2>Indicators</h2>
  <table><tbody>{{INDICATORS_HTML}}</tbody></table>

  <h2>Schedule</h2>
  {{SCHEDULE_HTML}}
</body>
</html>""",
        encoding="utf-8",
    )


def _ensure_excel_exists():
    if EXCEL_PATH.exists():
        return
    raise FileNotFoundError(
        f"Excel not found: {EXCEL_PATH}\n"
        f"Put US_data.xlsx in project root: {BASE_DIR}"
    )


def main():
    _ensure_dirs()
    _ensure_template()
    _ensure_excel_exists()

    out_path = OUTPUT_DIR / f"report_{ASOF}.html"

    html_path = generate_report(
        excel_path=str(EXCEL_PATH),
        asof_str=ASOF,
        gap=GAP,
        content_path=str(CONTENT_PATH),
        template_path=str(TEMPLATE_PATH),
        output_path=str(out_path),
    )

    print("[DONE]", html_path)

    # open in browser automatically
    webbrowser.open_new_tab(Path(html_path).resolve().as_uri())


if __name__ == "__main__":
    main()