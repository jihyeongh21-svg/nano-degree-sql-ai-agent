"""FRED에서 S&P 500 일별 종가를 받아 주간 종가와 요약 지표를 sp500_data.js로 만든다.

실행: python3 dashboard/scripts/build_sp500.py
"""
import csv
import json
import urllib.request
from datetime import date
from pathlib import Path

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500"

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache" / "sp500.csv"
OUT = HERE.parent / "sp500_data.js"


def load():
    if not CACHE.exists():
        CACHE.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(URL, CACHE)
    with open(CACHE, encoding="utf-8") as f:
        # 휴장일은 값이 비어 있다
        return [(date.fromisoformat(r["observation_date"]), float(r["SP500"]))
                for r in csv.DictReader(f) if r["SP500"].strip()]


def main():
    daily = load()

    # 주마다 마지막 거래일 종가. 등락률이 요약 지표와 맞도록 첫 거래일을 앞에 둔다
    weekly = {}
    for d, v in daily:
        weekly[d.isocalendar()[:2]] = (d, v)
    weekly = [daily[0]] + sorted(weekly.values())

    # 최대 낙폭: 직전 고점 대비 가장 크게 떨어진 구간 (일별 기준)
    peak = daily[0]
    mdd = (0.0, daily[0], daily[0])
    for d, v in daily:
        if v > peak[1]:
            peak = (d, v)
        dd = v / peak[1] - 1
        if dd < mdd[0]:
            mdd = (dd, peak, (d, v))

    # 연도별 수익률: 전년 마지막 종가 대비 해당 연도 마지막 종가
    year_end = {}
    for d, v in daily:
        year_end[d.year] = v
    years = sorted(year_end)
    yearly = [{"year": y, "close": year_end[y], "pct": round((year_end[y] / year_end[y - 1] - 1) * 100, 1)}
              for y in years[1:]]

    first, last = daily[0], daily[-1]
    span = (last[0] - first[0]).days / 365.25
    high = max(daily, key=lambda x: x[1])
    data = {
        "source": "FRED (Federal Reserve Bank of St. Louis), series SP500",
        "weekly": [[d.isoformat(), v] for d, v in weekly],
        "summary": {
            "first": [first[0].isoformat(), first[1]],
            "last": [last[0].isoformat(), last[1]],
            "high": [high[0].isoformat(), high[1]],
            "total_pct": round((last[1] / first[1] - 1) * 100, 1),
            "cagr_pct": round(((last[1] / first[1]) ** (1 / span) - 1) * 100, 1),
            "mdd_pct": round(mdd[0] * 100, 1),
            "mdd_peak": [mdd[1][0].isoformat(), mdd[1][1]],
            "mdd_trough": [mdd[2][0].isoformat(), mdd[2][1]],
        },
        "yearly": yearly,
    }
    OUT.write_text(
        "// build_sp500.py가 만든 파일. 직접 고치지 않는다.\nwindow.SP500_DATA = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps({k: data[k] for k in ("summary", "yearly")}, ensure_ascii=False, indent=1))
    print("weekly points:", len(weekly))


if __name__ == "__main__":
    main()
