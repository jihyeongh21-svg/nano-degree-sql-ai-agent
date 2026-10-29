# AI Agent 프로젝트: 주식투자 보조 대시보드

## 1. 프로젝트 소개
미국 지수·변동성·금리·환율 데이터를 모아 "지금 시장 분위기가 어떤가, 이번 달에도 적립식으로 사도 되나"를 한 화면에서 점검하는 웹 대시보드를 만들었습니다.
코드를 직접 짜지 않고 AI Agent인 Claude Code에게 한국어로 작업을 맡겨 데이터 수집, 집계, 화면 구현, 검증, 배포까지 진행했습니다.

- 기간: 2026-10-20 ~ 10-22 (오즈코딩스쿨 AI 헬스케어 3기 웹 대시보드 특강, 3일), 과제 마무리 10-29
- 데이터: FRED(Federal Reserve Bank of St. Louis) 공개 시리즈 7개 — `SP500`, `NASDAQCOM`, `DJIA`, `VIXCLS`, `DGS10`, `DGS2`, `DEXKOUS`
- **대시보드 모음**: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/
- **과제 1·2 대시보드**: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/invest/
- **빌드 1단계 그래프 (S&P 500)**: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/invest/sp500.html

> 투자 권유가 아닌 학습용 보조 자료입니다. 과거 수익률이 미래 수익을 보장하지 않습니다.

수업 시간에 건강보험 청구 데이터로 만든 대시보드와 그래프는 [9절 수업 실습](#9-수업-실습-건강보험-청구-데이터)에 정리했습니다.

## 2. 제작 목적
- **흩어진 지표를 한 화면에**: 지수, VIX, 금리, 환율을 각각 다른 사이트에서 찾아보지 않고 한 번에 봅니다.
- **감이 아니라 규칙으로 점검**: 200일선, RSI, VIX, 고점 대비 하락률처럼 널리 쓰이는 단순 규칙으로 상태를 표시해, 매수 전에 같은 기준으로 확인합니다.
- **원화 투자자 관점**: 미국 지수를 원화로 사는 경우를 가정해 환율 수준과 환율 변화까지 반영한 적립식 결과를 봅니다.
- **재현 가능한 결과물**: 집계 스크립트와 프롬프트를 남겨, 데이터가 갱신되면 같은 절차로 다시 만들 수 있게 합니다.

## 3. 사용 기술
- **Claude**: Claude Code
- **AI Agent 관련 기술**
  - 폴더 단위 작업: Agent가 폴더 안 파일을 직접 읽고 만들고 고침
  - 질의응답식 기획: Agent와 대화로 독자·KPI·차트를 정함
  - 단계별 프롬프트: 그래프 1개 → 지표 → 차트 → 시뮬레이터 순서로 한 번에 한 가지씩 요청 ([`PROMPTS.md`](PROMPTS.md))
- **기타 기술**
  - Python 표준 라이브러리 (CSV 다운로드, 이동평균·RSI·낙폭 계산)
  - HTML + Chart.js 4.4.1
  - Supabase + supabase-js 2.45.4 (데이터를 테이블에서 읽기, RLS 읽기 정책)
  - Windows Edge headless (화면 스크린샷 검증)
  - GitHub Pages (배포)

## 4. Agent 구조

```
[사용자] 한국어 요청 (PROMPTS.md)
   │
   ▼
[Claude Code]
   ├─ 데이터 받기 ──▶ FRED CSV 7개 → invest/scripts/.cache/*.csv
   ├─ 집계 ────────▶ invest/scripts/build_sp500.py  → sp500_data.js   (1단계)
   │                 invest/scripts/build_invest.py → invest_data.js  (2~4단계)
   ├─ 화면 생성 ───▶ invest/sp500.html (1단계 그래프) → invest/index.html (완성 대시보드)
   ├─ 검증 ────────▶ 요약 지표와 차트 값 대조, Edge headless 데스크톱·모바일 스크린샷
   ├─ DB 연결 ─────▶ market_daily.csv → Supabase 테이블 → 화면에서 supabase-js 로 읽어 계산
   └─ 배포 ────────▶ git push → GitHub Pages 공개 URL
```

### 빌드 과정
| 단계 | 한 일 | 결과물 |
| --- | --- | --- |
| 1. 그래프 1개 | S&P 500 10년 일별 종가를 받아 주간 꺾은선, 기간 버튼(1·3·5·10년), 최대 낙폭·연도별 수익률을 만듦 | [`invest/sp500.html`](invest/sp500.html), [`invest/scripts/build_sp500.py`](invest/scripts/build_sp500.py) |
| 2. 지표 추가 | 나스닥·다우·VIX·국채 10년/2년·원달러를 더 받아 지표 카드 6개와 시장 신호 6개를 만듦 | [`invest/scripts/build_invest.py`](invest/scripts/build_invest.py), [`invest/invest_data.js`](invest/invest_data.js) |
| 3. 차트 확장 | 50·200일선과 골든·데드크로스, 고점 대비 하락률, VIX, 장단기 금리차 차트 4개 | [`invest/index.html`](invest/index.html) |
| 4. 시뮬레이터 | 매달 투자금·시작 월·환율 반영 여부를 고르는 적립식 계산기 | [`invest/index.html`](invest/index.html) |
| 5. 검증·배포 | 숫자 대조, 스크린샷으로 겹침 확인, 문구 수정 후 GitHub Pages 배포 | 공개 URL |

### 폴더 구조
```
dashboard/
├── index.html        # 대시보드 모음 안내 페이지
├── README.md, PROMPTS.md, RETROSPECTIVE.md
├── invest/           # 과제 1·2: 주식투자 보조 대시보드
│   ├── index.html    # 완성 대시보드
│   ├── sp500.html    # 빌드 1단계 그래프
│   ├── invest_data.js, sp500_data.js
│   └── scripts/      # build_invest.py, build_sp500.py
└── claims/           # 수업 실습: 건강보험 청구 데이터
    ├── index.html    # 청구 대시보드
    ├── age-cost.html # 연령대별 진료비
    ├── data.js
    └── scripts/      # build_data.py
```

### 파일
| 파일 | 내용 |
| --- | --- |
| [`invest/index.html`](invest/index.html) | 과제 1·2: 주식투자 보조 대시보드 |
| [`invest/invest_data.js`](invest/invest_data.js) | 지수·VIX·금리·환율 집계 (자동 생성) |
| [`invest/scripts/build_invest.py`](invest/scripts/build_invest.py) | FRED 7개 시리즈 다운로드 + 집계, Supabase 업로드용 CSV 생성 |
| [`invest/supabase/market_daily.csv`](invest/supabase/market_daily.csv) | Supabase `market_daily` 테이블에 올릴 날짜별 지표 (2,576행, 자동 생성) |
| [`invest/sp500.html`](invest/sp500.html) | 빌드 1단계: S&P 500 주가 변동 그래프 |
| [`invest/sp500_data.js`](invest/sp500_data.js) | S&P 500 주간 종가·요약 (자동 생성) |
| [`invest/scripts/build_sp500.py`](invest/scripts/build_sp500.py) | FRED 다운로드 + 집계 |
| [`claims/index.html`](claims/index.html) | 수업 실습: 건강보험 청구 대시보드 |
| [`claims/age-cost.html`](claims/age-cost.html) | 수업 실습: 연령대별 진료비 그래프 |
| [`claims/data.js`](claims/data.js), [`claims/scripts/build_data.py`](claims/scripts/build_data.py) | 수업 실습용 청구 데이터 집계 (Supabase 연결 실패 시 백업) |
| [`claims/lookups.js`](claims/lookups.js) | 상병 한글명·종별 참조표 (자동 생성) |
| [`index.html`](index.html) | 대시보드 모음 안내 페이지 |
| [`PROMPTS.md`](PROMPTS.md) | 재현용 프롬프트 |
| [`RETROSPECTIVE.md`](RETROSPECTIVE.md) | 과제 3 회고 노트 |

## 5. 주요 기능
- **시장 신호 6개**: 추세(200일선), 모멘텀(RSI 14일), 변동성(VIX), 고점 대비 하락률, 장단기 금리차, 원/달러 환율(1년 평균 대비). 규칙에 따라 색 배지로 상태 표시
- **지표 카드 6개**: S&P 500·나스닥·다우·VIX·미 국채 10년·원/달러의 1일·1개월·연초 대비 변화 (금리는 %p)
- **추세 차트**: 최근 2년 S&P 500 종가와 50·200일선, 골든크로스(▲)·데드크로스(▼) 표시
- **위험 차트 3개**: 고점 대비 하락률 10년(−10%·−20% 기준선), VIX 2년(20·30 기준선), 10년−2년 금리차 2년
- **적립식 시뮬레이터**: 원화 투자금으로 매달 말 종가에 샀을 때 낸 돈·평가금·수익률과 추이, 연말 기준 표
- **접근성**: 라이트·다크 모드, 모바일 폭에서 한두 열로 재배치, 시뮬레이터 결과는 표로도 제공

### 신호 규칙
| 신호 | 기준 |
| --- | --- |
| 추세 | 종가가 200일선 위면 상승 추세, 아래면 하락 추세 |
| 모멘텀 | RSI(14일, Wilder) 70 이상 과열, 30 이하 과매도, 그 사이 중립 |
| 변동성 | VIX 15 미만 안정, 15~20 보통, 20~30 불안, 30 이상 공포 |
| 고점 대비 | 0 ~ −5% 고점 부근, −5 ~ −10% 숨 고르기, −10 ~ −20% 조정, −20% 이하 약세장 |
| 금리차 | 10년 − 2년이 0 미만이면 역전 |
| 환율 | 1년 평균보다 3% 넘게 높으면 달러 비쌈, 3% 넘게 낮으면 달러 쌈 |

## 6. 내가 수행한 내용
- **기획서 작성**: 이 페이지는 **원화로 미국 지수에 적립식 투자하는 개인 투자자** 가 **매달 매수 전** 에 **시장 분위기와 환율 부담을 점검** 하기 위해 봅니다.

  | 항목 | 내용 |
  | --- | --- |
  | 독자 | 원화로 미국 지수(S&P 500)에 적립식 투자하는 개인 |
  | 빈도 | 매달 매수 전 |
  | 목적 | 추세·과열·공포·환율을 점검하고 적립식 결과를 확인 |
  | KPI | 200일선 대비, RSI, VIX, 고점 대비 하락률, 금리차, 원/달러 |
  | 차트 | 이동평균 추세, 고점 대비 하락률, VIX, 금리차, 적립식 추이 |

- **빌드 순서 설계**: 그래프 1개(S&P 500)로 데이터·차트 틀을 먼저 확인한 뒤 지표와 차트를 늘려 대시보드로 확장
- **데이터 출처 결정**: 무료·무인증으로 받을 수 있는 FRED를 선택 (다른 시세 사이트는 브라우저 검증 페이지로 막힘)
- **신호 규칙 결정**: 널리 쓰이는 기준값을 정하고 화면에 규칙을 그대로 적음
- **숫자·문구 검증**: 요약 지표와 차트 값을 대조하고, 상황과 맞지 않는 문구를 고치도록 지시 (7절)
- **배포**: GitHub Pages로 공개 URL 확보

## 7. 테스트 및 개선

### 숫자 검증
| 항목 | 확인 내용 |
| --- | --- |
| 기간 등락률 | 1단계 그래프 범례(10년 +264.2%)와 위쪽 지표 "10년 상승률"(+264.2%)이 같음 |
| 연도별 수익률 | 연말 종가로 직접 계산한 값과 표가 같음 (2022년 −19.4%, 2019년 +28.9%) |
| 최대 낙폭 | 일별 기준 −33.9% (2020-02-19 → 2020-03-23). 주간 하락률 차트의 최저점은 −31.9%로, 주간 표본이라 조금 얕음 |
| 시뮬레이터 | 매달 50만 원 × 61개월 = 낸 돈 3,050만 원 |

### 화면 검증
Windows Edge headless로 1200px 폭과 모바일 폭 스크린샷을 찍어 라벨 겹침과 잘림이 없는지 확인했습니다.

### 막힌 점과 개선
| 문제 | 원인 | 개선 |
| --- | --- | --- |
| 시세 사이트에서 CSV를 받지 못함 | 자바스크립트 검증 페이지가 먼저 뜸 | FRED 공개 CSV(`fredgraph.csv?id=...`) 사용 |
| 휴장일 행에서 숫자 변환 오류 위험 | FRED는 휴장일 값을 비워 둠 | 빈 값과 `.` 은 건너뜀 |
| 범례 10년 등락률(+271.4%)과 위쪽 지표(+264.2%)가 다름 | 주간 데이터가 첫 거래일이 아니라 그 주 마지막 날부터 시작 | 첫 거래일을 주간 데이터 맨 앞에 넣음 |
| x축 연도 눈금이 2016, 2018, 2019… 로 고르지 않음 | 자동 눈금 건너뛰기 | 해(1년 구간은 달)가 바뀌는 첫 주에만 눈금 |
| 금리 카드 "연초 대비 +19.38%" 가 어색함 | 금리를 변화율로 계산 | 금리는 %p 차이로 표시 (+0.81%p) |
| 고점 대비 차트 연도 라벨이 붙어 보임 | 좁은 카드에 10년 라벨 10개 | 짝수 해만 표시 |
| VIX "보통" 이 초록 배지 | 15~20 구간도 안정과 같은 색 | 15~20은 회색(중립) |
| 환율 "달러 쌈" 인데 설명이 "살 때 부담" | 상황과 상관없이 같은 문장 | 비쌀 때·쌀 때 문장을 나눔 |
| 다크 모드에서 차트 색이 안 바뀜 | Chart.js 색은 그릴 때 한 번 정해짐 | 테마 변경 이벤트에서 차트를 다시 그림 |

## 8. 결과

### 주식투자 보조 대시보드 (과제 1·2)
- URL: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/invest/

| 신호 (기준일 2026-10-28) | 값 | 상태 |
| --- | --- | --- |
| 추세 | S&P 500 7,743.98, 200일선 7,302.71보다 +6.0% | 상승 추세 |
| 모멘텀 | RSI 53.0 | 중립 |
| 변동성 | VIX 17.52 (10-27) | 보통 |
| 고점 대비 | −1.0% (최고가 7,818.93) | 고점 부근 |
| 장단기 금리차 | 10년 4.99% − 2년 4.70% = +0.29%p | 정상 |
| 원/달러 | 1,325.06원 (10-23), 1년 평균 1,452.52원보다 −8.8% | 달러 쌈 |

- 마지막 교차: 2025-07-01 골든크로스 (그 전 2025-04-14 데드크로스)
- 최근 2년 VIX 최고 52.33 (2025-04-08), 20 이상이었던 날 110일(21%)
- 적립식 예시: 2021년 10월부터 매달 50만 원 → 낸 돈 3,050만 원, 평가금 4,556만 원(+49.4%, 환율 반영)

**인사이트**: 지금은 추세가 살아 있고 공포 신호가 없는 고점 부근입니다. 원/달러가 1년 평균보다 9% 가까이 낮아 원화로 사기에는 부담이 덜한 편입니다. 다만 고점 부근이므로 한 번에 몰아서 사기보다 정해 둔 금액을 나눠 사는 적립식이 맞습니다.

### Supabase 연결 (3일차 실습)
투자 대시보드도 고정된 집계(`invest_data.js`) 대신 Supabase 테이블에서 데이터를 읽어 브라우저에서 계산합니다. 차트와 화면은 그대로 두고 데이터 소스만 바꿨습니다.

1. **데이터 올리기**: `build_invest.py` 가 만든 [`invest/supabase/market_daily.csv`](invest/supabase/market_daily.csv) 를 Table Editor → Import data from CSV 로 `market_daily` 테이블에 올림
   - 열: `obs_date`(날짜), `sp500`, `nasdaq`, `dow`, `vix`, `us10y`, `us2y`, `usdkrw` — 날짜별 한 행, 발표가 없는 날은 빈 칸
   - 기간: S&P 500 첫 날짜 한 달 전(2016-09-30)부터 2,576행
2. **연결**: [`invest/index.html`](invest/index.html) 의 `SUPABASE_URL`, `SUPABASE_ANON_KEY` 에 Project URL·publishable 키를 넣음 (청구 대시보드와 같은 프로젝트)
3. **데이터가 안 보이면(RLS)**:
   ```sql
   alter table market_daily enable row level security;
   create policy "anon can read market_daily" on market_daily for select to anon using (true);
   ```
4. **확인**: Table Editor 에서 마지막 날 `sp500` 값을 바꾸고 새로고침 → 신호 카드와 차트가 바뀌면 성공
5. **후퇴 옵션**: 연결이 안 되면 머리말에 이유를 표시하고 `invest_data.js` 로 그림

구현 메모
- `build_invest.py` 의 계산(1일·1개월·연초 대비, 50·200일선, RSI, 골든·데드크로스, 고점 대비 하락률, 금리차, 환율 1년 평균, 월말 값)을 화면의 `buildData()` 로 옮김
- 파이썬 3.12 `sum()` 은 보정 덧셈(Neumaier)이라, JS 도 같은 방식으로 더해야 이동평균의 소수 둘째 자리 반올림이 같아짐 (처음에는 3곳이 0.01씩 달랐음)
- 1,000행씩 동시에 4개씩 읽고, 새로고침마다 최신 값을 읽도록 캐시를 쓰지 않으며 `accessToken` 으로 로그인 세션 확인을 건너뜀

검증 (실제 Supabase 연결 전)
- Supabase(PostgREST)처럼 응답하는 로컬 가짜 서버에 `market_daily.csv` 를 올리고 페이지 코드를 Node 에서 실행: `cards`·`signals`·`trend`·`crosses`·`drawdown`·`vix`·`spread`·`monthly` 8개 항목이 파이썬 `invest_data.js` 와 완전히 같음
- 마지막 날 S&P 500 을 7,743.98 → 7,000 으로 바꾸고 다시 읽으면 200일선 7,302.71 → 7,298.99, 고점 대비 −0.96% → −10.47%(조정)로 바뀌고, 되돌리면 원래 값
- 키 설정 전에는 브라우저에서 안내 문구와 함께 `invest_data.js` 로 정상 표시
- **실제 연결 (2026-10-29)**: Supabase 프로젝트의 `market_daily` 2,576행을 읽어 계산한 결과가 8개 항목 모두 `invest_data.js` 와 같음. CSV 가져오기에서 `sp500`·`dow` 열이 text 로 잡혔지만 화면에서 숫자로 바꿔 읽어 문제없음

### 빌드 1단계: S&P 500 주가 변동
- URL: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/invest/sp500.html
- 데이터: FRED `SP500` 일별 종가 2016-10-31 ~ 2026-10-28, 그래프는 주간 종가

| 지표 | 값 |
| --- | --- |
| 10년 상승률 | +264.2% (약 3.6배), 연평균 +13.8% |
| 최고가 | 7,818.93 (2026-10-06) |
| 최대 낙폭 | −33.9% (2020-02-19 → 2020-03-23, 코로나19) |
| 가장 나빴던 해 | 2022년 −19.4% |
| 가장 좋았던 해 | 2019년 +28.9% |

## 9. 수업 실습: 건강보험 청구 데이터
수업 시간(10/20~10/22)에 `kr_claims` 로 만든 결과물입니다. 데이터는 실제 환자 기록이 아닌 실습용 가상 데이터입니다.

### 청구 대시보드 ([`claims/index.html`](claims/index.html))
- URL: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/claims/
- 독자: 병원 경영기획팀장, 월초 경영회의 전날 전월 진료비와 환자 구성 점검
- KPI 카드 3개(명세서 수, 진료비, 수진자 수), 주상병 상위 10, 종별 건당 진료비, 월별 전체 vs 호흡기 꺾은선

| 결과 | 내용 |
| --- | --- |
| 규모 | 명세서 38,375건, 진료비 32.9억 원, 수진자 2,970명 |
| 상병 | 1위 급성 기관지염(J209) 5,285건, 2위 고혈압(I109) 4,403건 |
| 종별 | 명세서 79%가 의원. 건당 진료비는 상급종합병원 499,558원, 의원 36,019원으로 약 14배 |
| 계절성 | 호흡기 명세서 11~3월 대부분 월 700~840건, 6~9월 300~380건 |

숫자 검증: 총 명세서 수·진료비·수진자 수, 상급종합병원·의원 건당 진료비가 [SQL 실습 결과](../sql/README.md#6-결과)와 일치

#### Supabase 연결 (3일차 실습)
3일차 시연 프롬프트대로 명세서를 CSV 집계(`data.js`) 대신 Supabase `claim` 테이블에서 supabase-js(2.45.4)로 읽습니다. 차트는 그대로 두고 데이터 소스만 바꿨습니다.

1. **핸즈온 1**: Table Editor → Import data from CSV 로 `claim.csv` 를 `claim` 테이블로 올리고, Project Settings > API 에서 Project URL·anon key 확인
2. **연결**: [`claims/index.html`](claims/index.html) 의 `SUPABASE_URL`, `SUPABASE_ANON_KEY` 에 Project URL·publishable 키를 넣음
3. **데이터가 안 보이면(RLS)**: SQL Editor 에서 읽기 허용
   ```sql
   alter table claim enable row level security;
   create policy "anon can read claim" on claim for select to anon using (true);
   ```
4. **확인**: Table Editor 에서 한 행의 값을 바꾸고 새로고침 → 숫자가 바뀌면 성공
5. **후퇴 옵션**: 연결이 안 되면 머리말에 이유(설정 전 / RLS로 0행 / 오류)를 표시하고 저장해 둔 집계 `data.js` 로 그림

구현 메모
- Supabase는 한 번에 최대 1,000행을 돌려주므로 행 수를 먼저 세고 1,000행씩, 동시에 4개씩 필요한 열만 읽어 브라우저에서 집계
- 상병 한글명과 종별 이름은 `claim` 에 없어서 참조표 [`claims/lookups.js`](claims/lookups.js)(`build_data.py` 가 생성)로 붙임
- 새로고침마다 최신 값을 읽도록 요청에 `cache: "no-store"` 를 쓰고, 로그인이 필요 없으므로 공개 키를 `accessToken` 으로 바로 넘겨 supabase-js 의 로그인 세션 확인을 건너뜀 (세션 확인이 브라우저 잠금을 기다리다 멈추는 문제가 실제로 있었음)
- anon key는 공개 키라 화면 코드에 넣어도 되지만, service_role key는 절대 넣지 않음

검증 (실제 Supabase 연결 전)
- Supabase(PostgREST)처럼 응답하는 로컬 가짜 서버에 claim 38,375행을 올리고, 페이지의 연결·집계 코드를 그대로 Node에서 실행: KPI·종별 값이 `data.js` 와 같음
- 한 행의 진료비를 20,700원 → 1,000,020,700원으로 바꾸고 다시 읽으면 총 진료비 32.9억 → 42.9억, 의원 건당 36,019원 → 68,992원으로 바뀌고, 되돌리면 원래 값으로 돌아옴
- 설정 전·RLS로 0행일 때 `data.js` 로 대신 그리는 것은 브라우저에서 확인
- **실제 연결 (2026-10-29)**: Supabase 프로젝트의 `claim` 38,375행을 브라우저와 Node 에서 읽어 KPI·종별 값이 `data.js` 와 같음을 확인. 처음에는 테이블이 없거나(PGRST205) RLS 정책이 없어 0행이었고, CSV 가져오기와 `select` 정책 추가로 해결

### 연령대별 진료비 ([`claims/age-cost.html`](claims/age-cost.html))
- URL: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/claims/age-cost.html
- 40대부터 진료비가 크게 늘고, 남성 60대(2,284,035원)가 0~19세의 약 6.4배로 가장 높음

### 실습 중 막힌 점
| 문제 | 개선 |
| --- | --- |
| 로컬 MySQL에서 CSV를 내보내지 못함 (`ERROR 1045`) | 강의 백업 구글 시트에서 받고 행 수·합계로 같은 데이터인지 확인 |
| 인사이트 "11~3월 700~840건"이 2024년 1월(532건)과 안 맞음 | "11~3월 대부분" 으로 수정 |
| 종별 이름에 다른 코드가 섞일 위험 | `code_type = '종별코드'` 행만 사용 |

## 10. 배운 점
- **독자부터 정한다.** 누가, 언제, 무엇을 결정하려고 보는지 정해야 KPI와 차트가 정해집니다. 청구 대시보드와 투자 대시보드 모두 이 순서로 기획했습니다.
- **작게 만들고 키운다.** 그래프 1개로 데이터와 차트 틀을 먼저 확인하고, 거기에 지표와 차트를 붙여 대시보드로 키우니 막히는 곳을 빨리 찾을 수 있었습니다.
- **Agent에게는 작게 나눠 시킨다.** 한 번에 한 가지씩 요청해야 결과를 확인하고 되돌리기 쉽습니다.
- **Agent가 만든 숫자와 문장은 검증한다.** 범례와 지표의 등락률이 어긋나거나, 상황과 반대되는 설명 문장이 나오는 일이 있었습니다. 화면을 직접 보고 숫자를 맞춰 봐야 합니다.
- **규칙을 화면에 적는다.** 신호의 기준값을 화면에 그대로 적어 두면, 보는 사람이 신호를 맹신하지 않고 스스로 판단할 수 있습니다.
- **재현성을 남긴다.** 집계 스크립트와 프롬프트를 남기면 데이터가 갱신돼도 같은 절차로 다시 만들 수 있습니다.

## 11. GitHub
- 저장소: https://github.com/jihyeongh21-svg/nano-degree-sql-ai-agent
- 과제 1·2 대시보드: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/invest/
- 빌드 1단계 그래프 (S&P 500): https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/invest/sp500.html
- 수업 실습 청구 대시보드: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/claims/
- 수업 실습 연령대별 진료비: https://jihyeongh21-svg.github.io/nano-degree-sql-ai-agent/dashboard/claims/age-cost.html
- 실습·과제 SQL: [`sql/`](../sql/)
