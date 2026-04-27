"""공통 스타일 / 컬러 — 팔레트 업데이트"""

# ── 팔레트 1 (그린 계열) ──────────────────────
MINT        = '#8DD5C8'   # 연한 민트
SAGE_LIGHT  = '#8DC175'   # 연두/세이지
LEAF_GREEN  = '#4E9B5A'   # 나뭇잎 초록 (주컬러)
OLIVE       = '#4A5E35'   # 올리브
DEEP_GREEN  = '#2D3F38'   # 딥 다크 그린

# ── 팔레트 2 (웜/핑크 계열) ──────────────────
MAUVE       = '#9A7085'   # 모브/퍼플
SAGE_GREEN  = '#8DB8A5'   # 세이지 그린
CREAM       = '#DDE8C0'   # 크림/베이지
SALMON_LT   = '#F5B8A8'   # 연한 살몬
CORAL       = '#E87070'   # 코랄/살몬 레드

# ── 보조 ────────────────────────────────────
GRAY        = '#8A9E96'
LIGHT_GRAY  = '#F2F4F0'
WHITE       = '#FFFFFF'
MID_GREEN   = LEAF_GREEN

# ── 차트 컬러셋 ──────────────────────────────
# 메인 라인 계열 (선명, 구분 가능)
CHART_COLORS = [DEEP_GREEN, '#E65100', OLIVE, MAUVE, '#005F73', CORAL]

# Diverging (양수=그린, 음수=코랄) — 눈 안 아프게
COLOR_POS = LEAF_GREEN   # 양수
COLOR_NEG = CORAL        # 음수 (밝은 빨강 대신 코랄)

# 면적/그림자용 (차분)
FILL_PRIMARY   = f'rgba(141,193,117,0.18)'   # sage_light 투명
FILL_SECONDARY = f'rgba(221,232,192,0.35)'   # cream 투명
FILL_NEUTRAL   = f'rgba(138,158,150,0.15)'   # gray 투명

# 히트맵 컬러스케일
HEATMAP_GREEN  = [[0, '#DDE8C0'], [0.5, '#4E9B5A'], [1, '#2D3F38']]
HEATMAP_DIVERG = [[0, '#E87070'], [0.5, '#F2F4F0'], [1, '#4E9B5A']]

PLOTLY_TEMPLATE = 'plotly_white'

CSS = """
<style>
html, body, [class*="css"] {
    font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    color: #212121;
}
[data-testid="stSidebar"] {
    background-color: #F5F7F2;
    border-right: 1px solid #D8E4D0;
}
h1 { color: #2D3F38 !important; font-weight: 700 !important; letter-spacing: -0.3px; }
h2 { color: #2D3F38 !important; font-weight: 600 !important; }
h3 { color: #4A5E35 !important; font-weight: 600 !important; }
h4 { color: #4E9B5A !important; font-weight: 600 !important; }

/* 버튼 */
.stButton > button {
    background-color: #4E9B5A !important;
    color: white !important;
    border-radius: 4px !important;
    border: none !important;
    font-size: 13px !important;
}
.stButton > button:hover { background-color: #2D3F38 !important; }

/* 탭 */
.stTabs [data-baseweb="tab-list"] { gap: 2px; border-bottom: 1px solid #D8E4D0; }
.stTabs [data-baseweb="tab"] {
    border-radius: 4px 4px 0 0;
    padding: 7px 18px;
    font-size: 13px;
    color: #6B7B6E;
}
.stTabs [aria-selected="true"] {
    background-color: #F5F7F2 !important;
    color: #2D3F38 !important;
    border-bottom: 2px solid #4E9B5A !important;
    font-weight: 600 !important;
}

/* 구분선 */
hr { border-color: #D8E4D0 !important; margin: 16px 0 !important; }

/* selectbox/radio */
.stSelectbox label, .stRadio label, .stMultiSelect label {
    font-size: 12px !important;
    color: #5A6B60 !important;
    font-weight: 500 !important;
}

/* metric */
[data-testid="metric-container"] {
    background: #F5F7F2;
    border: 1px solid #D8E4D0;
    border-radius: 4px;
    padding: 10px 14px;
}
</style>
"""

def view_badge_html(view: str) -> str:
    cfg = {
        'OW':  ('#E8F2E4', '#2D3F38', '비중확대'),
        'NW':  ('#F2F4F0', '#5A6B60', '중립'),
        'UW':  ('#F5E8E4', '#8A3030', '비중축소'),
    }
    bg, fg, label = cfg.get(view, ('#F2F4F0', '#333', view))
    return f'<span style="background:{bg};color:{fg};border-radius:3px;padding:2px 9px;font-weight:700;font-size:12px">{label}</span>'
