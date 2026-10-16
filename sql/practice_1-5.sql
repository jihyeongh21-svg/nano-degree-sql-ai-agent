-- 수업 실습 1~5 (3일 동안 쓴 쿼리)

-- ============================================================
-- [실습 1] 2025년 12월 외래 명세서에 상병 이름 붙이기 (JOIN, WHERE, ORDER BY)
-- ============================================================
USE kr_claims;

SELECT c.mid, c.recu_fr_dd, c.main_sick, s.krnm, c.rvd_rpe_tamt_amt
FROM claim c
JOIN sick_master s ON s.sickcd = c.main_sick
WHERE c.fom_tp_cd = '031'
  AND c.recu_fr_dd BETWEEN '2025-12-01' AND '2025-12-31'
ORDER BY c.rvd_rpe_tamt_amt DESC
LIMIT 10;

-- ============================================================
-- [실습 2] 종별 진료비 비교 (GROUP BY, HAVING, 다중 JOIN)
-- ============================================================
SELECT t.code_nm AS cl_nm,
       COUNT(*) AS claims,
       ROUND(AVG(c.rvd_rpe_tamt_amt)) AS avg_total,
       ROUND(SUM(c.rvd_slf_brdn_amt) * 100 / SUM(c.rvd_rpe_tamt_amt), 1) AS self_pct
FROM claim c
JOIN institution i ON i.yid = c.yid
JOIN code_table t ON t.code_type = '종별코드' AND t.code = i.cl_cd
GROUP BY t.code_nm
ORDER BY avg_total DESC;

-- ============================================================
-- [실습 3] 고혈압(I109) 환자의 방문 간격 (윈도우 함수)
-- ============================================================
WITH v AS (
  SELECT jid, recu_fr_dd,
         ROW_NUMBER() OVER (PARTITION BY jid ORDER BY recu_fr_dd) AS visit_no,
         DATEDIFF(recu_fr_dd, LAG(recu_fr_dd) OVER (PARTITION BY jid ORDER BY recu_fr_dd)) AS gap_days,
         SUM(rvd_rpe_tamt_amt) OVER (PARTITION BY jid ORDER BY recu_fr_dd) AS cum_amt
  FROM claim
  WHERE main_sick = 'I109' AND fom_tp_cd = '031'
)
SELECT * FROM v
WHERE gap_days > 90
ORDER BY gap_days DESC;

-- ============================================================
-- [실습 4] 폐암 진단 연도별 1년 안 사망률 (CTE, LEFT JOIN)
-- ============================================================
USE kr_lung_cancer;

WITH cohort AS (
  SELECT pt_sbst_no,
         bspt_frst_diag_ymd AS index_dd,
         YEAR(bspt_frst_diag_ymd) AS diag_year
  FROM lung_pt_bsnf
  WHERE bspt_frst_diag_ymd >= '2010-01-01' AND bspt_frst_diag_ymd < '2020-01-01'
),
outcome AS (
  SELECT c.pt_sbst_no, c.diag_year,
         CASE WHEN d.dead_ymd <= c.index_dd + INTERVAL 365 DAY THEN 1 ELSE 0 END AS dead_1y
  FROM cohort c
  LEFT JOIN lung_dead_nfrm d ON d.pt_sbst_no = c.pt_sbst_no
)
SELECT diag_year,
       COUNT(*) AS patients,
       SUM(dead_1y) AS dead_1y,
       ROUND(AVG(dead_1y) * 100, 1) AS dead_1y_pct
FROM outcome
GROUP BY diag_year
ORDER BY diag_year;

-- ============================================================
-- [실습 5] 병기에 따른 치료 경로 (CASE)
-- ============================================================
SELECT CASE WHEN bspt_stag_vl IN ('0', '1', '2') THEN '1) 초기 (0~2기)'
            WHEN bspt_stag_vl = '3' THEN '2) 국소 진행 (3기)'
            WHEN bspt_stag_vl = '4' THEN '3) 전이 (4기)'
            ELSE '4) 병기 미상' END AS stage_group,
       COUNT(*) AS patients,
       ROUND(AVG(CASE WHEN bspt_frst_oprt_ymd IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS surgery_pct,
       ROUND(AVG(CASE WHEN bspt_frst_ancn_trtm_strt_ymd IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS chemo_pct,
       ROUND(AVG(CASE WHEN bspt_frst_rdt_strt_ymd IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS radiation_pct,
       ROUND(AVG(CASE WHEN bspt_dead_ymd IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS dead_pct
FROM lung_pt_bsnf
GROUP BY stage_group
ORDER BY stage_group;
