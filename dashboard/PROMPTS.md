# 재현용 프롬프트

과제 1·2 제출용입니다. 아래 프롬프트를 순서대로 Claude Code에 입력하면 같은 결과를 다시 만들 수 있습니다.
작업 폴더는 이 저장소의 `dashboard/` 입니다.

## 0. 데이터 준비

```
kr_claims 백업 구글 시트(ID 1nPuY8AKFAs2r9da4xUBV3WMKdLEBZJGpmd3kP7xKNvU)에서
claim, institution, sick_master, code_table, patient 탭을 CSV로 받아 scripts/.cache/ 에 저장해줘.
gviz CSV 내보내기 주소(/gviz/tq?tqx=out:csv&sheet=<탭이름>)를 쓰고,
받은 뒤 claim 행 수(38,375), 진료비 합계, 고유 jid 수를 출력해서 SQL 결과와 맞는지 확인해줘.
```

> 로컬 MySQL에 접속할 수 있으면 DBeaver에서 각 테이블을 CSV로 내보내도 됩니다.

## 1. 집계 스크립트

```
scripts/build_data.py 를 만들어줘. 표준 라이브러리만 쓰고, scripts/.cache/ 의 CSV를 읽어
dashboard/data.js 에 window.DASHBOARD_DATA 로 아래 집계를 넣어줘.
- kpi: 명세서 수, 진료비 합계(rvd_rpe_tamt_amt), 수진자 수(jid 고유)
- top_sick: main_sick 별 명세서 수 상위 10, sick_master.krnm 한글명
- by_type: yid 로 institution 을 붙여 cl_cd 를 얻고, code_table 에서 code_type = '종별코드' 인 행으로 이름을 바꿔
  종별 명세서 수, 건당 평균 진료비, 본인부담률(rvd_slf_brdn_amt 합 / 진료비 합)
- monthly: recu_fr_dd 월별 전체 명세서 수와 main_sick 이 J 로 시작하는 명세서 수
- age_cost: 환자별 2년 진료비 합계를 patient 의 성별(sex_tp_cd)·연령대(2025년 기준, 0-19/20-39/40-59/60-69/70+)로 묶은 평균
```

## 2. 과제 2: 대시보드 (`index.html`)

```
data.js 를 읽는 index.html 대시보드를 만들어줘. Chart.js 4.4.1(cdnjs)을 쓰고 다른 파일은 만들지 마.
독자는 병원 경영기획팀장, 월초 경영회의 전날에 전월 진료비와 환자 구성을 점검하려고 본다. 이 문장을 상단에 넣어줘.
- KPI 카드 3개: 총 명세서 수, 총 진료비(억 원), 수진자 수
- 주상병별 명세서 수 상위 10 가로 막대
- 종별 건당 평균 진료비 세로 막대 (툴팁에 명세서 수, 본인부담률)
- 월별 꺾은선: 전체 vs 호흡기 질환(J) 두 선, 축은 하나만
- 차트마다 "표로 보기" 펼침 표
- 맨 아래 "인사이트:" 한 줄
라이트·다크 모드 색은 CSS 변수로 두고, 모바일 폭에서는 한 열로 쌓아줘.
```

```
인사이트를 숫자로 채워줘. 의원 명세서 비중, 상급종합병원과 의원의 건당 진료비 배수,
호흡기 명세서의 겨울(11~3월)과 여름(6~9월) 범위를 data.js 값으로 계산해서 써줘.
2024년 1월처럼 범위를 벗어나는 달이 있으면 "대부분" 처럼 표현을 맞춰줘.
```

## 3. 과제 1: 관심 주제 그래프 (`age-cost.html`)

```
data.js 의 age_cost 로 age-cost.html 을 만들어줘. 제목은 "나이가 들수록 진료비는 얼마나 늘어날까".
연령대별 남성·여성 환자 1명당 2년 진료비를 묶음 막대로 그리고, 툴팁에 환자 수를 같이 보여줘.
그래프 아래에 0~19세 대비 가장 높은 연령대의 배수를 자동 계산해 한 줄로 써줘.
스타일은 index.html 과 같게 맞춰줘.
```

## 4. 확인

```
Edge headless 로 index.html 과 age-cost.html 스크린샷을 찍어서 라벨 겹침, 잘림이 없는지 확인해줘.
KPI 숫자가 SQL 결과(38,375건, 3,293,580,300원, 2,970명)와 같은지,
종별 건당 진료비가 SQL 실습 2 결과(상급종합병원 499,558원, 의원 36,019원)와 같은지도 확인해줘.
```

## 5. 배포

```
dashboard 폴더를 커밋해서 main 에 push 하고, 저장소 GitHub Pages 를 main 브랜치 / (root) 로 켜줘.
대시보드 공개 URL 을 알려줘.
```
