# 크레딧 리서치 엔진 (Credit Research Engine)

## 빠른 시작

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 실행
streamlit run app.py
```

## 구조

```
credit_research/
├── app.py                  # 메인 진입점
├── requirements.txt
├── data/
│   └── loader.py           # Excel 파싱 (Wide→Long format)
├── scoring/
│   └── engine.py           # 스코어링 엔진 (OW/NW/UW)
├── pages/
│   ├── market_view.py      # Page 1: 금리/스프레드 차트
│   ├── sector_matrix.py    # Page 2: 섹터 매트릭스 + 히트맵
│   ├── credit_flow.py      # Page 3: 발행/수요예측/등급 수동입력
│   └── report_builder.py  # Page 4: 리포트 자동생성
└── assets/
    └── styles.py           # 테마/컬러
```

## 데이터 형식

- Wide-format Excel (시가평가 3사평균)
- 섹터: 공사/공단채, 은행채, 카드채, 기타금융채, 회사채
- 등급: AAA ~ A+
- 만기: 3M, 6M, 9M, 1Y, 1.5Y, 2Y, 2.5Y, 3Y, 4Y, 5Y

## 스코어링 엔진

```
total_score = rate_level + spread_level + momentum + vol

≥ +2 → OW (Overweight)
≤ -2 → UW (Underweight)
else → NW (Neutral Weight)
```

## 확장 예정

- `base_score` 현재 구현
- `macro_score` 추가 가능 (거시지표 연결)
- `flow_score` 추가 가능 (발행 데이터 크롤러)
- `rating_score` 추가 가능 (신용등급 이벤트)

## 저장 파일

- `credit_flow_data.json`: Credit Flow 입력 데이터
- `report_data.json`: Report Builder 코멘트 데이터
