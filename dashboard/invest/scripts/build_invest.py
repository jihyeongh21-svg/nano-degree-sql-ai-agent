"""FRED에서 지수·변동성·금리·환율을 받아 투자 보조 대시보드용 invest_data.js를 만든다.
Supabase Table Editor 에 올릴 market_daily.csv(날짜별 한 행)도 함께 만든다.

실행: python3 dashboard/invest/scripts/build_invest.py
"""
import csv
import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path

SERIES = {
    "sp500": "SP500",       # S&P 500
    "nasdaq": "NASDAQCOM",  # 나스닥 종합
    "dow": "DJIA",          # 다우존스 산업평균
    "vix": "VIXCLS",        # 변동성 지수
    "us10y": "DGS10",       # 미 국채 10년 금리(%)
    "us2y": "DGS2",         # 미 국채 2년 금리(%)
    "usdkrw": "DEXKOUS",    # 원/달러 환율
}

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
OUT = HERE.parent / "invest_data.js"
OUT_CSV = HERE.parent / "supabase" / "market_daily.csv"


def load(series_id):
    path = CACHE / f"{series_id}.csv"
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        urllib.request.urlretrieve(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", path)
    with open(path, encoding="utf-8") as f:
        rows = csv.DictReader(f)
        col = rows.fieldnames[1]
        # 휴장일은 값이 비어 있거나 "."
        return [(date.fromisoformat(r["observation_date"]), float(r[col]))
                for r in rows if r[col].strip() not in ("", ".")]


def value_on_or_before(series, d):
    for x, v in reversed(series):
        if x <= d:
            return v
    return series[0][1]


def changes(series, rate=False):
    """최근 값과 1일·1개월·연초 대비 변화. 금리는 %p 차이, 나머지는 변화율(%)"""
    last_d, last_v = series[-1]
    prev = series[-2][1]
    month = value_on_or_before(series, last_d - timedelta(days=30))
    ytd = value_on_or_before(series, date(last_d.year - 1, 12, 31))
    diff = (lambda base: round(last_v - base, 2)) if rate else (lambda base: round((last_v / base - 1) * 100, 2))
    return {"date": last_d.isoformat(), "value": last_v, "d1": diff(prev), "m1": diff(month), "ytd": diff(ytd)}


def sma(values, n):
    return [round(sum(values[i - n + 1:i + 1]) / n, 2) if i >= n - 1 else None for i in range(len(values))]


def rsi(values, n=14):
    """Wilder 방식 RSI의 마지막 값"""
    gains = [max(values[i] - values[i - 1], 0) for i in range(1, len(values))]
    losses = [max(values[i - 1] - values[i], 0) for i in range(1, len(values))]
    avg_g, avg_l = sum(gains[:n]) / n, sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        avg_g, avg_l = (avg_g * (n - 1) + g) / n, (avg_l * (n - 1) + l) / n
    return round(100 - 100 / (1 + avg_g / avg_l), 1) if avg_l else 100.0


def month_end(series):
    out = {}
    for d, v in series:
        out[(d.year, d.month)] = (d, v)
    return [out[k] for k in sorted(out)]


def main():
    s = {k: load(v) for k, v in SERIES.items()}
    sp = s["sp500"]
    closes = [v for _, v in sp]

    ma50, ma200 = sma(closes, 50), sma(closes, 200)

    # 50일선이 200일선을 위·아래로 뚫은 날
    crosses = []
    for i in range(200, len(sp)):
        before, now = ma50[i - 1] - ma200[i - 1], ma50[i] - ma200[i]
        if before <= 0 < now:
            crosses.append([sp[i][0].isoformat(), "golden"])
        elif before >= 0 > now:
            crosses.append([sp[i][0].isoformat(), "dead"])

    # 고점 대비 하락률 (주간 표본)
    peak, dd_weekly, weekly = 0, [], {}
    for d, v in sp:
        peak = max(peak, v)
        weekly[d.isocalendar()[:2]] = [d.isoformat(), round((v / peak - 1) * 100, 2)]
    dd_weekly = [weekly[k] for k in sorted(weekly)]

    # 최근 2년 일별: 종가, 50일선, 200일선
    start = sp[-1][0] - timedelta(days=730)
    trend = [[d.isoformat(), v, ma50[i], ma200[i]] for i, (d, v) in enumerate(sp) if d >= start]
    since = lambda series: [[d.isoformat(), v] for d, v in series if d >= start]

    spread = [[d.isoformat(), round(v - value_on_or_before(s["us2y"], d), 2)]
              for d, v in s["us10y"] if d >= start]

    # 적립식 계산용 월말 값: S&P 500과 같은 달 환율
    monthly = [[f"{d.year}-{d.month:02d}", v, value_on_or_before(s["usdkrw"], d)] for d, v in month_end(sp)]

    fx_1y = [v for d, v in s["usdkrw"] if d >= s["usdkrw"][-1][0] - timedelta(days=365)]

    data = {
        "source": "FRED (Federal Reserve Bank of St. Louis): " + ", ".join(SERIES.values()),
        "cards": {k: changes(v, rate=k in ("us10y", "us2y")) for k, v in s.items()},
        "signals": {
            "sp_close": closes[-1],
            "ma50": ma50[-1],
            "ma200": ma200[-1],
            "rsi14": rsi(closes),
            "drawdown": dd_weekly[-1][1],
            "high": max(closes),
            "vix": s["vix"][-1][1],
            "spread": spread[-1][1],
            "usdkrw": s["usdkrw"][-1][1],
            "usdkrw_1y_avg": round(sum(fx_1y) / len(fx_1y), 2),
            "last_cross": crosses[-1] if crosses else None,
        },
        "trend": trend,
        "crosses": [c for c in crosses if c[0] >= start.isoformat()],
        "drawdown": dd_weekly,
        "vix": since(s["vix"]),
        "spread": spread,
        "monthly": monthly,
    }
    OUT.write_text(
        "// build_invest.py가 만든 파일. 직접 고치지 않는다.\nwindow.INVEST_DATA = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps({"cards": data["cards"], "signals": data["signals"], "crosses": data["crosses"]},
                     ensure_ascii=False, indent=1))
    print("trend", len(trend), "drawdown", len(dd_weekly), "monthly", len(monthly), "bytes", OUT.stat().st_size)
    write_market_csv(s)


def write_market_csv(s):
    """S&P 500 첫 날짜 한 달 전부터, 날짜별로 7개 지표를 한 행에 담는다. 값이 없는 칸은 비워 둔다."""
    since = s["sp500"][0][0] - timedelta(days=31)
    by_date = {}
    for key, series in s.items():
        for d, v in series:
            if d >= since:
                by_date.setdefault(d, {})[key] = v
    OUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["obs_date", *SERIES])
        for d in sorted(by_date):
            w.writerow([d.isoformat(), *(by_date[d].get(k, "") for k in SERIES)])
    print("market_daily.csv rows", len(by_date))


if __name__ == "__main__":
    main()
