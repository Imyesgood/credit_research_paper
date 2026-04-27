"""
크레딧 데이터 로더
Wide-format Excel → Long-format DataFrame
"""
import pandas as pd
import re
import streamlit as st

TENORS = ['3월이하', '6월이하', '9월이하', '1년이하', '1.5년이하', '2년이하', '2.5년이하', '3년이하', '4년이하', '5년이하']
TENOR_LABELS = ['3M', '6M', '9M', '1Y', '1.5Y', '2Y', '2.5Y', '3Y', '4Y', '5Y']
TENOR_MAP = dict(zip(TENORS, TENOR_LABELS))

SECTOR_MAP = {
    '공사/공단채': '공사/공단채',
    '은행채': '은행채',
    '카드채': '카드채',
    '기타금융채': '기타금융채',
    '회사채': '회사채',
}

def parse_category(raw: str):
    raw = raw.replace('시가평가 3사평균 ', '').replace('(공모/무보증)', '').strip()
    raw = raw.replace('AA0', 'AA')
    
    if '공사/공단채' in raw:
        sector = '공사/공단채'
        rating = raw.replace('공사/공단채 ', '').strip()
    elif '은행채' in raw:
        sector = '은행채'
        rating = raw.split('은행채 ')[-1].strip()
    elif '카드채' in raw:
        sector = '카드채'
        rating = raw.split('카드채 ')[-1].strip()
    elif '기타금융채' in raw:
        sector = '기타금융채'
        rating = raw.replace('기타금융채', '').strip()
    elif '회사채' in raw:
        sector = '회사채'
        rating = raw.replace('회사채', '').strip()
    else:
        sector = raw
        rating = ''
    
    return sector, rating


@st.cache_data(show_spinner=False)
def load_excel(file_bytes: bytes) -> pd.DataFrame:
    import io
    raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, header=None)
    n_blocks = raw.shape[1] // 11
    
    frames = []
    for b in range(n_blocks):
        base = b * 11
        cat_raw = str(raw.iloc[0, base]).strip()
        if cat_raw == 'nan':
            continue
        sector, rating = parse_category(cat_raw)
        
        block = raw.iloc[2:, base:base+11].copy()
        block.columns = ['date'] + TENORS
        block = block.dropna(subset=['date'])
        block['date'] = pd.to_datetime(block['date'], errors='coerce')
        block = block.dropna(subset=['date'])
        
        melted = block.melt(id_vars='date', var_name='tenor_raw', value_name='yield')
        melted['tenor'] = melted['tenor_raw'].map(TENOR_MAP)
        melted['sector'] = sector
        melted['rating'] = rating
        melted['category'] = f"{sector} {rating}"
        melted = melted.dropna(subset=['yield'])
        melted['yield'] = pd.to_numeric(melted['yield'], errors='coerce')
        frames.append(melted[['date', 'sector', 'rating', 'category', 'tenor', 'yield']])
    
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values('date')
    return df


def get_spread(df: pd.DataFrame, cat_a: str, cat_b: str, tenor: str) -> pd.DataFrame:
    """cat_a 금리 - cat_b 금리 = spread (bps)"""
    a = df[(df['category'] == cat_a) & (df['tenor'] == tenor)].set_index('date')['yield']
    b = df[(df['category'] == cat_b) & (df['tenor'] == tenor)].set_index('date')['yield']
    spread = ((a - b) * 100).rename('spread')
    return spread.dropna().reset_index()


def get_curve(df: pd.DataFrame, category: str, date: pd.Timestamp) -> pd.DataFrame:
    tenor_order = TENOR_LABELS
    sub = df[(df['category'] == category) & (df['date'] == date)].copy()
    sub['tenor_order'] = sub['tenor'].map({t: i for i, t in enumerate(tenor_order)})
    return sub.sort_values('tenor_order')


def get_mom_change(df: pd.DataFrame, category: str, tenor: str) -> pd.Series:
    sub = df[(df['category'] == category) & (df['tenor'] == tenor)].set_index('date')['yield']
    sub = sub.sort_index()
    mom = (sub - sub.shift(21)) * 100  # ~1개월 전 대비 (bps)
    return mom.dropna()
