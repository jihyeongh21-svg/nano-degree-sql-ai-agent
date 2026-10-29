"""kr_claims 백업 시트에서 CSV를 받아 대시보드용 집계를 data.js로 만든다.

실행: python3 dashboard/claims/scripts/build_data.py
"""
import csv
import json
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SHEET_ID = "1nPuY8AKFAs2r9da4xUBV3WMKdLEBZJGpmd3kP7xKNvU"
TABLES = ["claim", "institution", "sick_master", "code_table", "patient"]

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
OUT = HERE.parent / "data.js"

# 연령은 데이터 마지막 해(2025년) 기준
BASE_YEAR = 2025
AGE_BANDS = ["0-19", "20-39", "40-59", "60-69", "70+"]


def load(table):
    path = CACHE / f"{table}.csv"
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={table}"
        urllib.request.urlretrieve(url, path)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def age_band(birth_yr):
    age = BASE_YEAR - int(birth_yr)
    if age < 20:
        return "0-19"
    if age < 40:
        return "20-39"
    if age < 60:
        return "40-59"
    if age < 70:
        return "60-69"
    return "70+"


def main():
    claim = load("claim")
    institution = {r["yid"]: r for r in load("institution")}
    sick_name = {r["sickcd"]: r["krnm"] for r in load("sick_master")}
    cl_name = {r["code"]: r["code_nm"] for r in load("code_table") if r["code_type"] == "종별코드"}
    patient = {r["jid"]: r for r in load("patient")}

    amt = lambda r: int(r["rvd_rpe_tamt_amt"])

    kpi = {
        "claims": len(claim),
        "total_amt": sum(amt(r) for r in claim),
        "patients": len({r["jid"] for r in claim}),
    }

    sick_cnt = Counter(r["main_sick"] for r in claim)
    top_sick = [
        {"code": code, "name": sick_name.get(code, code), "claims": n}
        for code, n in sick_cnt.most_common(10)
    ]

    # 종별 이름은 code_type = '종별코드' 행에서만 찾는다
    by_cl = defaultdict(lambda: [0, 0, 0])
    for r in claim:
        name = cl_name[institution[r["yid"]]["cl_cd"]]
        by_cl[name][0] += 1
        by_cl[name][1] += amt(r)
        by_cl[name][2] += int(r["rvd_slf_brdn_amt"])
    by_type = sorted(
        (
            {
                "name": name,
                "claims": n,
                "avg_amt": round(total / n),
                "self_pct": round(slf * 100 / total, 1),
            }
            for name, (n, total, slf) in by_cl.items()
        ),
        key=lambda x: -x["avg_amt"],
    )

    monthly = defaultdict(lambda: [0, 0])
    for r in claim:
        ym = r["recu_fr_dd"][:7]
        monthly[ym][0] += 1
        if r["main_sick"].startswith("J"):
            monthly[ym][1] += 1
    monthly = [{"month": ym, "all": a, "resp": j} for ym, (a, j) in sorted(monthly.items())]

    # 과제 1: 연령대·성별 환자 1명당 2년 진료비
    person_amt = defaultdict(int)
    for r in claim:
        person_amt[r["jid"]] += amt(r)
    age_cost = {sex: {b: [0, 0] for b in AGE_BANDS} for sex in ("1", "2")}
    for jid, total in person_amt.items():
        p = patient[jid]
        cell = age_cost[p["sex_tp_cd"]][age_band(p["birth_yr"])]
        cell[0] += 1
        cell[1] += total
    age_cost = {
        "bands": AGE_BANDS,
        "male": [{"patients": n, "avg_amt": round(t / n) if n else 0} for n, t in age_cost["1"].values()],
        "female": [{"patients": n, "avg_amt": round(t / n) if n else 0} for n, t in age_cost["2"].values()],
    }

    data = {
        "kpi": kpi,
        "top_sick": top_sick,
        "by_type": by_type,
        "monthly": monthly,
        "age_cost": age_cost,
    }
    OUT.write_text(
        "// build_data.py가 만든 파일. 직접 고치지 않는다.\nwindow.DASHBOARD_DATA = "
        + json.dumps(data, ensure_ascii=False, indent=1)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(data, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
