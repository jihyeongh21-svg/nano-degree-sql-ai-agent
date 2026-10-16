-- 과제 3. 병기 그룹별 3년 안 사망률
USE kr_lung_cancer;

-- Q1. 2010-01-01 ~ 2017-12-31 진단 환자 수
SELECT COUNT(*) AS patients
FROM lung_pt_bsnf
WHERE bspt_frst_diag_ymd >= '2010-01-01' AND bspt_frst_diag_ymd < '2018-01-01';

-- Q2. 병기 그룹 4개별 진단 뒤 3년(1095일) 안 사망 비율
WITH cohort AS (
  SELECT pt_sbst_no, bspt_frst_diag_ymd AS index_dd,
         CASE WHEN bspt_stag_vl IN ('0', '1', '2') THEN '1) 초기 (0~2기)'
              WHEN bspt_stag_vl = '3' THEN '2) 국소 진행 (3기)'
              WHEN bspt_stag_vl = '4' THEN '3) 전이 (4기)'
              ELSE '4) 병기 미상' END AS stage_group
  FROM lung_pt_bsnf
  WHERE bspt_frst_diag_ymd >= '2010-01-01' AND bspt_frst_diag_ymd < '2018-01-01'
),
outcome AS (
  SELECT c.pt_sbst_no, c.stage_group,
         CASE WHEN d.dead_ymd <= c.index_dd + INTERVAL 1095 DAY THEN 1 ELSE 0 END AS dead_3y
  FROM cohort c
  LEFT JOIN lung_dead_nfrm d ON d.pt_sbst_no = c.pt_sbst_no
)
SELECT stage_group, COUNT(*) AS patients, SUM(dead_3y) AS dead_3y,
       ROUND(AVG(dead_3y) * 100, 1) AS dead_3y_pct
FROM outcome
GROUP BY stage_group
ORDER BY stage_group;
