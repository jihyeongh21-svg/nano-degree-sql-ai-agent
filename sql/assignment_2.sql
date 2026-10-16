-- 과제 2. 상병별 집계와 당뇨병 환자의 방문 간격
USE kr_claims;

-- Q1. 2024년 외래 명세서를 주상병별로 묶어 명세서 수, 환자 수, 환자 1명당 명세서 수 (상위 5개)
SELECT c.main_sick, s.krnm,
       COUNT(*) AS claims,
       COUNT(DISTINCT c.jid) AS patients,
       ROUND(COUNT(*) / COUNT(DISTINCT c.jid), 2) AS claims_per_patient
FROM claim c
JOIN sick_master s ON s.sickcd = c.main_sick
WHERE c.fom_tp_cd = '031'
  AND c.recu_fr_dd BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.main_sick, s.krnm
ORDER BY claims DESC
LIMIT 5;

-- Q2. 같은 조건에서 명세서가 500건 이상인 상병만
SELECT c.main_sick, s.krnm,
       COUNT(*) AS claims,
       COUNT(DISTINCT c.jid) AS patients,
       ROUND(COUNT(*) / COUNT(DISTINCT c.jid), 2) AS claims_per_patient
FROM claim c
JOIN sick_master s ON s.sickcd = c.main_sick
WHERE c.fom_tp_cd = '031'
  AND c.recu_fr_dd BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.main_sick, s.krnm
HAVING COUNT(*) >= 500
ORDER BY claims DESC;

-- Q3. 당뇨병(E119) 외래 방문 중 직전 방문과의 간격이 90일을 넘은 방문
WITH v AS (
  SELECT jid, recu_fr_dd,
         ROW_NUMBER() OVER (PARTITION BY jid ORDER BY recu_fr_dd) AS visit_no,
         DATEDIFF(recu_fr_dd, LAG(recu_fr_dd) OVER (PARTITION BY jid ORDER BY recu_fr_dd)) AS gap_days,
         SUM(rvd_rpe_tamt_amt) OVER (PARTITION BY jid ORDER BY recu_fr_dd) AS cum_amt
  FROM claim
  WHERE main_sick = 'E119' AND fom_tp_cd = '031'
)
SELECT * FROM v
WHERE gap_days > 90
ORDER BY gap_days DESC;
