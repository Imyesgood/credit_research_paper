from dataclasses import dataclass

@dataclass(frozen=True)
class SeriesSpec:
    sheet: str
    block: str
    value_col: str

@dataclass(frozen=True)
class BondSeriesSpec:
    sheet: str
    block: str

@dataclass(frozen=True)
class ReportItemConfig:
    spec: SeriesSpec | BondSeriesSpec
    use_diff: bool = False
    is_bond: bool  = False
    fmt: str       = "price"
    diff_fmt: str  = "pct2"

def _bond(block: str) -> ReportItemConfig:
    return ReportItemConfig(
        spec=BondSeriesSpec(sheet="국내채권", block=block),
        use_diff=True,
        is_bond=True,
        fmt="rate_kr",
        diff_fmt="absbp2",
    )

REPORT_ITEM_CONFIG: dict[str, ReportItemConfig] = {
    # 국내채권 (BondSeries)
    "통안 2Y":   _bond("통안 2Y"),
    "국고 3Y":   _bond("국고 3Y"),
    "국고 5Y":   _bond("국고 5Y"),
    "국고 10Y":  _bond("국고 10Y"),

    # 선물
    "국채3년선물": ReportItemConfig(
        spec=SeriesSpec(sheet="국내채권", block="3년국채 연결", value_col="현재가"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),

    # 환율
    "USD/KRW": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="서울외환(기업용) USDKRW 스팟 (~15:30)", value_col="현재가"),
        use_diff=False, fmt="fx", diff_fmt="pct2",
    ),
    "NDF": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="NDF 뉴욕 NDF 뉴욕", value_col="NDF_MID_Close"),
        use_diff=False, fmt="fx", diff_fmt="pct2",
    ),
    "Dollar Index": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="달러인덱스 DOLLARS", value_col="KR_MID_Close"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "USD/JPY": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="서울외환 이종통화 USDJPY", value_col="Close"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "EUR/USD": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="서울외환 이종통화 EURUSD", value_col="Close"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "JPY/KRW": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="서울외환 이종통화 JPYKRW", value_col="Close"),
        use_diff=False, fmt="fx", diff_fmt="pct2",
    ),
    "USD/CNY": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="중국:USDCNY:뉴욕종가", value_col="현재가"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "GBP/USD": ReportItemConfig(
        spec=SeriesSpec(sheet="환율", block="영국:GBPUSD:뉴욕종가", value_col="현재가"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),

    # 주가지수
    "KOSPI": ReportItemConfig(
        spec=SeriesSpec(sheet="주가지수", block="KOSPI", value_col="현재가"),
        use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "NIKKEI": ReportItemConfig(
        spec=SeriesSpec(sheet="주가지수", block="니케이 225", value_col="현재가"),
        use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "DOW": ReportItemConfig(
        spec=SeriesSpec(sheet="주가지수", block="다우", value_col="현재가"),
        use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "NASDAQ": ReportItemConfig(
        spec=SeriesSpec(sheet="주가지수", block="나스닥", value_col="현재가"),
        use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "S&P500": ReportItemConfig(
        spec=SeriesSpec(sheet="주가지수", block="S&P 500", value_col="현재가"),
        use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "중국상해종합": ReportItemConfig(
        spec=SeriesSpec(sheet="지수", block="중국:상하이종합지수", value_col="현재가"),
        use_diff=False, fmt="index", diff_fmt="pct2",
    ),

    # 해외채권 (절대차)
    "T-Note (2yr)": ReportItemConfig(
        spec=SeriesSpec(sheet="해외채권", block="2년 T-NOTE", value_col="현재가"),
        use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "T-Note (10yr)": ReportItemConfig(
        spec=SeriesSpec(sheet="해외채권", block="10년 T-NOTE", value_col="현재가"),
        use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "T-Bill (30yr)": ReportItemConfig(
        spec=SeriesSpec(sheet="해외채권", block="30년 T-BOND", value_col="현재가"),
        use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),

    # 원자재
    "WTI": ReportItemConfig(
        spec=SeriesSpec(sheet="원자재", block="WTI 현물", value_col="현재가"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "GOLD": ReportItemConfig(
        spec=SeriesSpec(sheet="원자재", block="금 고시가격 USD 온스 PM", value_col="현재가"),
        use_diff=False, fmt="price", diff_fmt="pct2",
    ),

    # SOFR / TED
    "SOFR": ReportItemConfig(
        spec=SeriesSpec(sheet="외환", block="미국:SOFR(SECURED OVERNIGHT FINANCING RATE)", value_col="현재가"),
        use_diff=True, fmt="rate_idx", diff_fmt="abs4",
    ),
    "TED spread": ReportItemConfig(
        spec=SeriesSpec(sheet="지수", block="미국:TED스프레드", value_col="현재가"),
        use_diff=True, fmt="rate_idx", diff_fmt="abs4",
    ),
}