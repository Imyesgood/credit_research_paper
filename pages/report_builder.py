"""
Page 4: Report Builder
자동 리서치 멘트 생성 + 수동 수정
"""
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from data.loader import TENOR_LABELS, get_spread, get_mom_change
from scoring.engine import compute_score
from assets.styles import DEEP_GREEN, LEAF_GREEN, GRAY

REPORT_SAVE_PATH = "report_data.json"


def _load_report() -> dict:
    if os.path.exists(REPORT_SAVE_PATH):
        try:
            with open(REPORT_SAVE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def _save_report(data: dict):
    with open(REPORT_SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _auto_generate_comment(df, cat, tenor, sp_base):
    s = df[(df['category'] == cat) & (df['tenor'] == tenor)]
    if len(s) == 0:
        return "데이터 없음"
    
    ys = s.set_index('date')['yield'].sort_index()
    
    # 스프레드 계산
    sp_df = get_spread(df, cat, sp_base, tenor)
    sp_series = sp_df.set_index('date')['spread'] if len(sp_df) > 0 else None
    
    sc = compute_score(ys, sp_series)
    
    last_yield = ys.iloc[-1]
    prev_1m_yield = ys.iloc[-22] if len(ys) >= 22 else ys.iloc[0]
    mom_bp = (last_yield - prev_1m_yield) * 100
    
    pct = sc['rate_pct'] * 100
    
    comment = f"""[{cat} | {tenor}]
현재 금리: {last_yield:.3f}% (1Y 분위 {pct:.0f}%ile)
전월 대비: {'+' if mom_bp >= 0 else ''}{mom_bp:.1f}bp {'상승' if mom_bp >= 0 else '하락'}
투자의견: {sc['view']} (Score: {sc['total_score']})
{sc['comment']}"""
    
    return comment


def render(df: pd.DataFrame):
    st.header("Report Builder")
    st.caption("자동 생성 후 수동 수정 가능 | 저장 시 유지됩니다")

    all_cats = sorted(df['category'].unique().tolist())
    default_base = next((c for c in all_cats if '공사/공단채 AAA' in c), all_cats[0])

    saved = _load_report()
    if saved.get('last_saved'):
        st.info(f"마지막 저장: {saved['last_saved']}", icon="💾")

    with st.sidebar:
        st.markdown("### ⚙️ 리포트 설정")
        report_tenor = st.selectbox("기준 만기", TENOR_LABELS, index=TENOR_LABELS.index('3Y'), key='rp_tenor')
        sp_base_rp = st.selectbox("스프레드 기준", all_cats,
                                   index=all_cats.index(default_base) if default_base in all_cats else 0,
                                   key='rp_sp_base')
        report_date = datetime.now().strftime('%Y년 %m월')

    # ── 섹션별 편집 ────────────────────────────────────────
    tab_titles = ["🏠 Market Overview", "📊 섹터별 의견", "🔮 전략 요약"]
    tab1, tab2, tab3 = st.tabs(tab_titles)

    # ─ TAB 1: Market Overview ─────────────────────────────
    with tab1:
        st.markdown("#### 시장 총평")
        
        # 자동 생성
        if st.button("자동 생성", key='auto_overview'):
            # 주요 지표 요약
            sample_cats = [c for c in all_cats if '회사채 AA-' in c or '회사채 AA+' in c or '은행채 AAA' in c][:3]
            auto_lines = []
            for cc in sample_cats:
                s = df[(df['category'] == cc) & (df['tenor'] == report_tenor)]
                if len(s) > 0:
                    ys = s.set_index('date')['yield'].sort_index()
                    sc = compute_score(ys)
                    last = ys.iloc[-1]
                    auto_lines.append(f"- {cc}: {last:.3f}% | {sc['view']}")
            
            auto_text = f"""{report_date} 크레딧 채권 시장 총평

국내 크레딧 채권 시장은 금리 변동성이 지속되는 가운데, 섹터별 스프레드 차별화가 나타나고 있다.

주요 지표 현황 ({report_tenor} 기준):
""" + '\n'.join(auto_lines) + """

시장 전반의 투자 환경은 [시장 상황에 따라 수정]하며, 
향후 [전망 내용]이 예상된다."""
            
            st.session_state['overview_text'] = auto_text

        overview = st.text_area(
            "시장 총평",
            value=st.session_state.get('overview_text', saved.get('overview', '')),
            height=350,
            key='overview_input',
            label_visibility='collapsed'
        )

    # ─ TAB 2: 섹터별 의견 ────────────────────────────────
    with tab2:
        st.markdown("#### 섹터별 투자의견")
        
        # 분석 대상 선택
        report_cats = st.multiselect(
            "분석 카테고리 선택",
            all_cats,
            default=saved.get('report_cats', [c for c in all_cats if '회사채' in c][:5]),
            key='report_cats'
        )

        # 자동 생성
        if st.button("전체 자동 생성", key='auto_sector'):
            for cc in report_cats:
                auto_comment = _auto_generate_comment(df, cc, report_tenor, sp_base_rp)
                st.session_state[f'sector_{cc}'] = auto_comment

        # 각 카테고리별 편집
        sector_texts = {}
        for cc in report_cats:
            st.markdown(f"---")
            
            # 스코어 표시
            s = df[(df['category'] == cc) & (df['tenor'] == report_tenor)]
            if len(s) > 0:
                ys = s.set_index('date')['yield'].sort_index()
                sc = compute_score(ys)
                vcol = {'OW': '#1B5E20', 'NW': '#616161', 'UW': '#C62828'}[sc['view']]
                vbg = {'OW': '#E8F5E9', 'NW': '#F5F5F5', 'UW': '#FFEBEE'}[sc['view']]
                
                header_col, auto_col = st.columns([4, 1])
                with header_col:
                    st.markdown(f"""<div style="display:flex; align-items:center; gap:10px">
                        <span style="font-weight:700; color:{DEEP_GREEN}; font-size:15px">{cc}</span>
                        <span style="background:{vbg}; color:{vcol}; border-radius:12px; padding:2px 12px; font-weight:900; font-size:14px">{sc['view']}</span>
                        <span style="color:{GRAY}; font-size:12px">Score: {sc['total_score']}</span>
                    </div>""", unsafe_allow_html=True)
                with auto_col:
                    if st.button("🤖", key=f'auto_{cc}', help="자동 생성"):
                        auto_c = _auto_generate_comment(df, cc, report_tenor, sp_base_rp)
                        st.session_state[f'sector_{cc}'] = auto_c

            default_val = st.session_state.get(f'sector_{cc}', saved.get(f'sector_{cc}', ''))
            if not default_val and len(s) > 0:
                default_val = _auto_generate_comment(df, cc, report_tenor, sp_base_rp)

            sector_texts[cc] = st.text_area(
                f"{cc} 코멘트",
                value=default_val,
                height=150,
                key=f'sector_input_{cc}',
                label_visibility='collapsed'
            )

    # ─ TAB 3: 전략 요약 ──────────────────────────────────
    with tab3:
        st.markdown("#### 전략 요약 및 투자의견")
        
        if st.button("자동 생성", key='auto_strategy'):
            # 스코어 집계
            ow_cats, uw_cats, nw_cats = [], [], []
            for cc in report_cats if report_cats else all_cats[:10]:
                s = df[(df['category'] == cc) & (df['tenor'] == report_tenor)]
                if len(s) > 0:
                    ys = s.set_index('date')['yield'].sort_index()
                    sc = compute_score(ys)
                    if sc['view'] == 'OW':
                        ow_cats.append(cc)
                    elif sc['view'] == 'UW':
                        uw_cats.append(cc)
                    else:
                        nw_cats.append(cc)
            
            strategy_auto = f"""{report_date} 크레딧 채권 전략 요약

■ Overweight (OW)
{chr(10).join('- ' + c for c in ow_cats) if ow_cats else '- 해당 없음'}

■ Neutral Weight (NW)
{chr(10).join('- ' + c for c in nw_cats) if nw_cats else '- 해당 없음'}

■ Underweight (UW)
{chr(10).join('- ' + c for c in uw_cats) if uw_cats else '- 해당 없음'}

■ 핵심 전략
[전략 내용을 여기에 수정 입력]

■ 주요 리스크
- [리스크 1]
- [리스크 2]"""
            
            st.session_state['strategy_text'] = strategy_auto

        strategy = st.text_area(
            "전략 요약",
            value=st.session_state.get('strategy_text', saved.get('strategy', '')),
            height=450,
            key='strategy_input',
            label_visibility='collapsed'
        )

    # ── 저장 버튼 ──────────────────────────────────────────
    st.markdown("---")
    col_s1, col_s2, col_s3 = st.columns([1, 1, 4])
    with col_s1:
        if st.button("저장", type='primary', use_container_width=True, key='save_report'):
            data = {
                'overview': st.session_state.get('overview_input', ''),
                'strategy': st.session_state.get('strategy_input', ''),
                'report_cats': st.session_state.get('report_cats', []),
                'last_saved': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            for cc in report_cats:
                data[f'sector_{cc}'] = st.session_state.get(f'sector_input_{cc}', '')
            _save_report(data)
            st.success("저장 완료!")
            st.rerun()

    # ── 리포트 미리보기 ──────────────────────────────────
    st.markdown("---")
    with st.expander("리포트 전체 미리보기"):
        preview_text = f"""{'='*60}
크레딧 채권 리서치 | {report_date}
{'='*60}

【시장 총평】
{st.session_state.get('overview_input', saved.get('overview', ''))}

【섹터별 의견】
"""
        for cc in report_cats:
            v = st.session_state.get(f'sector_input_{cc}', saved.get(f'sector_{cc}', ''))
            if v:
                preview_text += f"\n{v}\n"
        
        preview_text += f"""
【전략 요약】
{st.session_state.get('strategy_input', saved.get('strategy', ''))}

{'='*60}
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        st.text_area("미리보기", value=preview_text, height=600, label_visibility='collapsed')
        st.download_button("텍스트 다운로드", preview_text,
                           file_name=f"credit_research_{datetime.now().strftime('%Y%m%d')}.txt",
                           mime='text/plain')
