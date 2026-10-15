-- 03_analysis.sql
-- Descriptive analysis of the default rate. Each block is saved as a CSV in results/.

-- name: overall_default_rate
SELECT
    COUNT(*)                               AS n_clients,
    SUM(default_next_month)                AS n_defaults,
    ROUND(AVG(default_next_month) * 100, 2) AS default_rate_pct
FROM clients;

-- name: default_by_last_repayment_status
-- The most recent repayment status is usually the strongest risk signal.
SELECT
    CASE
        WHEN pay_0 <= -1 THEN 'paid on time'
        WHEN pay_0 = 0   THEN 'revolving'
        WHEN pay_0 = 1   THEN '1 month late'
        WHEN pay_0 = 2   THEN '2 months late'
        ELSE '3+ months late'
    END                                     AS last_status,
    COUNT(*)                                AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2) AS default_rate_pct
FROM clients
GROUP BY last_status
ORDER BY default_rate_pct;

-- name: default_by_age_band
SELECT
    CASE
        WHEN age < 30 THEN '21-29'
        WHEN age < 40 THEN '30-39'
        WHEN age < 50 THEN '40-49'
        WHEN age < 60 THEN '50-59'
        ELSE '60+'
    END                                     AS age_band,
    COUNT(*)                                AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2) AS default_rate_pct
FROM clients
GROUP BY age_band
ORDER BY age_band;

-- name: default_by_education
SELECT
    CASE education
        WHEN 1 THEN 'graduate school'
        WHEN 2 THEN 'university'
        WHEN 3 THEN 'high school'
        ELSE 'other / unknown'
    END                                     AS education_level,
    COUNT(*)                                AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2) AS default_rate_pct
FROM clients
GROUP BY education_level
ORDER BY default_rate_pct DESC;

-- name: default_by_credit_limit_quintile
-- Window function: split clients into 5 groups of equal size by credit limit.
WITH ranked AS (
    SELECT
        limit_bal,
        default_next_month,
        NTILE(5) OVER (ORDER BY limit_bal) AS limit_quintile
    FROM clients
)
SELECT
    limit_quintile,
    MIN(limit_bal)                          AS min_limit,
    MAX(limit_bal)                          AS max_limit,
    COUNT(*)                                AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2) AS default_rate_pct
FROM ranked
GROUP BY limit_quintile
ORDER BY limit_quintile;
