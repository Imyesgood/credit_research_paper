"""
Page 2: Sector Matrix
섹터 x 등급 x 만기 히트맵 + 투자의견 스코어카드
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data.loader import TENOR_LABELS
from scoring.engine import compute_score
from assets.styles import (DEEP_GREEN, LEAF_GREEN, GRAY, OLIVE,
                            HEATMAP_GREEN, HEATMAP_DIVERG, PLOTLY_TEMPLATE)


def render(df: pd.DataFrame):
    st.header("Sector Matrix")

    all_cats = sorted(df['category'].unique().tolist())
    default_base = next((c for c in all_cats if '공사/공단채 AAA' in c), all_cats[0])

    mf1, mf2, mf3 = st.columns([1, 2, 3])
    with mf1:
        sel_tenor_mx = st.selectbox("기준 만기", TENOR_LABELS,
                                     index=TENOR_LABELS.index('3Y'), key='mx_tenor')
    with mf2:
        show_mode = st.radio("표시 값", ['금리(%)', '스프레드(bp)'],
                              horizontal=True, key='mx_mode')
    with mf3:
        sp_base = st.selectbox("스프레드 기준 계열", all_cats,
                                index=all_cats.index(default_base) if default_base in all_cats else 0,
                                key='mx_base')

    sectors = sorted(df['sector'].unique().tolist())
    all_ratings = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-']

    # ── 매트릭스 빌드 ──────────────────────────────────────
    matrix_data = {}
    for cat in all_cats:
        s = df[(df['category'] == cat) & (df['tenor'] == sel_tenor_mx)]
        sub = df[df['category'] == cat]
        sec = sub['sector'].iloc[0] if len(sub) > 0 else ''
        rat = sub['rating'].iloc[0] if len(sub) > 0 else ''
        if len(s) == 0:
            continue
        last_yield = s.iloc[-1]['yield']
        if show_mode == '스프레드(bp)':
            base = df[(df['category'] == sp_base) & (df['tenor'] == sel_tenor_mx)]
            base_yield = base.iloc[-1]['yield'] if len(base) > 0 else np.nan
            val = round((last_yield - base_yield) * 100, 1) if not np.isnan(last_yield) and not np.isnan(base_yield) else np.nan
        else:
            val = round(last_yield, 3) if not np.isnan(last_yield) else np.nan
        matrix_data[(sec, rat)] = val

    rating_order = [r for r in all_ratings if any(rat == r for _, rat in matrix_data.keys())]
    suffix = '%' if show_mode == '금리(%)' else 'bp'

    # ── 히트맵 ────────────────────────────────────────────
    z_vals, hover_text = [], []
    for sec in sectors:
        row_z, row_h = [], []
        for rat in rating_order:
            v = matrix_data.get((sec, rat), np.nan)
            row_z.append(v if isinstance(v, float) and not np.isnan(v) else np.nan)
            row_h.append(f"{sec} {rat}: {v}{suffix}" if isinstance(v, float) and not np.isnan(v) else '-')
        z_vals.append(row_z)
        hover_text.append(row_h)

    cs = HEATMAP_GREEN if show_mode == '금리(%)' else HEATMAP_DIVERG

    fig = go.Figure(go.Heatmap(
        z=z_vals, x=rating_order, y=sectors,
        text=[[f"{v:.2f}" if not np.isnan(v) else '-' for v in row] for row in z_vals],
        texttemplate="%{text}",
        hovertext=hover_text, hoverinfo='text',
        colorscale=cs, showscale=True,
        colorbar=dict(title=dict(text=suffix, side='right'), thickness=12, len=0.8)
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, height=300,
        title=dict(text=f"섹터 매트릭스  |  {sel_tenor_mx}  |  {show_mode}",
                   font=dict(color=DEEP_GREEN, size=13), x=0),
        font=dict(family="Apple SD Gothic Neo, Noto Sans KR, sans-serif", size=11),
        margin=dict(l=110, r=30, t=48, b=30),
        xaxis=dict(side='top'),
        plot_bgcolor='white', paper_bgcolor='white',
    )
    st.plotly_chart(fig, use_container_width=True)

    # 테이블
    rows_tbl = []
    for sec in sectors:
        row = {'섹터': sec}
        for rat in rating_order:
            v = matrix_data.get((sec, rat), np.nan)
            row[rat] = f"{v:.2f}{suffix}" if isinstance(v, float) and not np.isnan(v) else '-'
        rows_tbl.append(row)
    st.dataframe(pd.DataFrame(rows_tbl).set_index('섹터'), use_container_width=True)

    # ── 투자의견 스코어카드 ───────────────────────────────
    st.markdown("---")
    st.markdown("#### 투자의견")

    score_cats = st.multiselect(
        "분석 계열 선택", all_cats,
        default=[c for c in all_cats if '회사채' in c][:4],
        key='score_cats'
    )

    if score_cats:
        VIEW_CFG = {
            'OW': {'label': '비중확대', 'bg': '#EEF4EB', 'fg': '#2D3F38', 'border': '#8DC175'},
            'NW': {'label': '중립',    'bg': '#F2F4F0', 'fg': '#5A6B60', 'border': '#B0BDB4'},
            'UW': {'label': '비중축소','bg': '#F5EDEB', 'fg': '#8A3030', 'border': '#E0A898'},
        }
        cols = st.columns(min(len(score_cats), 3))
        for i, cc in enumerate(score_cats):
            s = df[(df['category'] == cc) & (df['tenor'] == sel_tenor_mx)]
            if len(s) == 0:
                continue
            ys = s.set_index('date')['yield'].sort_index()
            sc = compute_score(ys)
            cfg = VIEW_CFG.get(sc['view'], VIEW_CFG['NW'])

            with cols[i % 3]:
                st.markdown(f"""
<div style="border:1px solid {cfg['border']};border-radius:5px;padding:14px 16px;
            margin:6px 0;background:{cfg['bg']}">
  <div style="font-size:12px;color:#6B7B6E;font-weight:500;margin-bottom:4px">{cc}</div>
  <div style="font-size:18px;font-weight:700;color:{cfg['fg']};margin-bottom:8px">{cfg['label']}</div>
  <div style="font-size:11px;color:#555;line-height:1.9">
    금리 레벨&nbsp;&nbsp;{sc['rate_pct']*100:.0f}%ile &nbsp;({sc['rate_score']:+d})<br>
    스프레드&nbsp;&nbsp;&nbsp;{sc['spread_pct']*100:.0f}%ile &nbsp;({sc['spread_score']:+d})<br>
    모멘텀 Z&nbsp;&nbsp;&nbsp;{sc['momentum_z']:.2f} &nbsp;({sc['momentum_score']:+d})<br>
    변동성&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;({sc['vol_score']:+d})<br>
    <span style="font-weight:600">합계&nbsp;&nbsp;{sc['total_score']:+d}</span>
  </div>
  <div style="font-size:10px;color:#888;margin-top:8px;padding-top:6px;
              border-top:1px solid {cfg['border']}">{sc['comment']}</div>
</div>""", unsafe_allow_html=True)

    # ── 카테고리 x 만기 히트맵 ──────────────────────────
    st.markdown("---")
    st.markdown("#### 카테고리 x 만기 히트맵")

    hm_cats = st.multiselect("계열", all_cats, default=all_cats[:8], key='hm_cats')
    hm_mode = st.radio("값", ['금리(%)', '1M 변화(bp)'], horizontal=True, key='hm_mode')

    if hm_cats:
        hm_z, hm_text = [], []
        for cc in hm_cats:
            rz, rt = [], []
            for tn in TENOR_LABELS:
                s = df[(df['category'] == cc) & (df['tenor'] == tn)]
                if len(s) == 0:
                    rz.append(np.nan); rt.append('-'); continue
                if hm_mode == '금리(%)':
                    v = s.iloc[-1]['yield']
                    rz.append(v); rt.append(f"{v:.3f}%")
                else:
                    ys2 = s.set_index('date')['yield'].sort_index()
                    v = (ys2.iloc[-1] - ys2.iloc[-22]) * 100 if len(ys2) >= 22 else np.nan
                    rz.append(v); rt.append(f"{v:.1f}bp" if not np.isnan(v) else '-')
            hm_z.append(rz); hm_text.append(rt)

        cs2 = HEATMAP_GREEN if hm_mode == '금리(%)' else HEATMAP_DIVERG

        fig_hm = go.Figure(go.Heatmap(
            z=hm_z, x=TENOR_LABELS, y=hm_cats,
            text=hm_text, texttemplate="%{text}",
            hovertemplate="%{y} %{x}: %{text}<extra></extra>",
            colorscale=cs2, showscale=True,
        ))
        fig_hm.update_layout(
            template=PLOTLY_TEMPLATE,
            height=max(280, len(hm_cats) * 34 + 90),
            title=dict(text=f"카테고리 x 만기  |  {hm_mode}",
                       font=dict(color=DEEP_GREEN, size=13), x=0),
            font=dict(family="Apple SD Gothic Neo, Noto Sans KR, sans-serif", size=10),
            margin=dict(l=190, r=30, t=48, b=30),
            xaxis=dict(side='top'),
            plot_bgcolor='white', paper_bgcolor='white',
        )
        st.plotly_chart(fig_hm, use_container_width=True)
