-- 과제 1. 2025년 7월 외래 명세서 읽기
USE kr_claims;

-- Q1. 2025년 7월에 시작한 외래(031) 명세서 수
SELECT COUNT(*) AS claims
FROM claim
WHERE fom_tp_cd = '031'
  AND recu_fr_dd BETWEEN '2025-07-01' AND '2025-07-31';

-- Q2. 7월 외래 명세서에 상병 한글명을 붙이고 진료비 큰 순으로 정렬
SELECT c.mid, c.recu_fr_dd, c.main_sick, s.krnm, c.rvd_rpe_tamt_amt
FROM claim c
JOIN sick_master s ON s.sickcd = c.main_sick
WHERE c.fom_tp_cd = '031'
  AND c.recu_fr_dd BETWEEN '2025-07-01' AND '2025-07-31'
ORDER BY c.rvd_rpe_tamt_amt DESC
LIMIT 10;

-- Q3. 2년 전체 입원(021) 명세서를 입내원일수 긴 순으로 정렬하고 상병 한글명 붙이기
SELECT c.mid, c.recu_fr_dd, c.recu_to_dd, c.main_sick, s.krnm, c.vst_ddcnt
FROM claim c
JOIN sick_master s ON s.sickcd = c.main_sick
WHERE c.fom_tp_cd = '021'
ORDER BY c.vst_ddcnt DESC
LIMIT 10;
