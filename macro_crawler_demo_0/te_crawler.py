# te_crawler.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

COUNTRIES = [
    "australia", "indonesia", "india", "brazil",
    "south-africa", "mexico", "russia"
]

INDICATORS = {
    "Inflation Rate": "inflation-cpi",
    "Interest Rate": "interest-rate",
}

HEADERS = ["Calendar", "GMT", "Reference", "Actual", "Previous", "Consensus", "TEForecast"]


def clean(x):
    if pd.isna(x):
        return ""
    return str(x).replace("\xa0", " ").strip()


def extract_calendar_table(html):
    soup = BeautifulSoup(html, "lxml")

    for table in soup.find_all("table"):
        try:
            df = pd.read_html(StringIO(str(table)))[0]
        except Exception:
            continue

        df.columns = [clean(c) for c in df.columns]

        if all(h in df.columns for h in HEADERS):
            return df

    # fallback: Trading Economics가 table 태그 없이 텍스트로 렌더링될 때
    text = soup.get_text("\n")
    if "Calendar" not in text or "TEForecast" not in text:
        return None

    lines = [clean(x) for x in text.splitlines() if clean(x)]
    rows = []

    for i, line in enumerate(lines):
        # 날짜로 시작하는 행 탐색
        if len(line) == 10 and line[4] == "-" and line[7] == "-":
            chunk = lines[i:i + 8]
            if len(chunk) < 6:
                continue

            calendar = chunk[0]
            gmt = chunk[1] if i + 1 < len(lines) else ""

            # Reference는 보통 Jan, Feb 같은 월 문자열
            ref_idx = None
            for j in range(i + 2, min(i + 8, len(lines))):
                if lines[j] in [
                    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                    "Q1", "Q2", "Q3", "Q4"
                ]:
                    ref_idx = j
                    break

            if ref_idx is None:
                continue

            values = lines[ref_idx + 1: ref_idx + 5]
            while len(values) < 4:
                values.append("")

            rows.append({
                "Calendar": calendar,
                "GMT": gmt,
                "Reference": lines[ref_idx],
                "Actual": values[0],
                "Previous": values[1],
                "Consensus": values[2],
                "TEForecast": values[3],
            })

    return pd.DataFrame(rows) if rows else None


def latest_actual_row(df):
    df = df.copy()
    df["Actual"] = df["Actual"].map(clean)
    df = df[df["Actual"] != ""]

    if df.empty:
        return None

    df["Calendar_dt"] = pd.to_datetime(df["Calendar"], errors="coerce")
    df = df.sort_values("Calendar_dt", ascending=False)

    return df.iloc[0]


def crawl():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            channel="chrome"  # 설치된 Chrome 사용
        )
        page = browser.new_page()

        for country in COUNTRIES:
            for indicator_name, slug in INDICATORS.items():
                url = f"https://tradingeconomics.com/{country}/{slug}"
                print(f"Fetching: {url}")

                page.goto(url, wait_until="networkidle", timeout=60000)
                html = page.content()

                df = extract_calendar_table(html)

                if df is None:
                    results.append({
                        "country": country,
                        "indicator": indicator_name,
                        "status": "calendar_table_not_found",
                        "url": url,
                    })
                    continue

                row = latest_actual_row(df)

                if row is None:
                    results.append({
                        "country": country,
                        "indicator": indicator_name,
                        "status": "no_actual_value",
                        "url": url,
                    })
                    continue

                results.append({
                    "country": country,
                    "indicator": indicator_name,
                    "calendar": clean(row["Calendar"]),
                    "gmt": clean(row["GMT"]),
                    "reference": clean(row["Reference"]),
                    "actual": clean(row["Actual"]),
                    "previous": clean(row["Previous"]),
                    "consensus": clean(row["Consensus"]),
                    "url": url,
                    "status": "ok",
                })

        browser.close()

    out = pd.DataFrame(results)
    out.to_csv("tradingeconomics_latest.csv", index=False, encoding="utf-8-sig")
    print(out)
    print("\nSaved: tradingeconomics_latest.csv")


if __name__ == "__main__":
    crawl()