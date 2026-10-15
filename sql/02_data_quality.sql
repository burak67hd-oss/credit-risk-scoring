-- 02_data_quality.sql
-- Each query returns one check. The Python script prints them all.

-- name: row_count
SELECT COUNT(*) AS n_rows FROM clients;

-- name: duplicate_ids
SELECT COUNT(*) - COUNT(DISTINCT id) AS n_duplicates FROM clients;

-- name: missing_values
SELECT
    SUM(limit_bal IS NULL) + SUM(age IS NULL) + SUM(pay_0 IS NULL)
  + SUM(bill_amt1 IS NULL) + SUM(pay_amt1 IS NULL) AS n_missing_key_fields
FROM clients;

-- name: undocumented_education_codes
SELECT education, COUNT(*) AS n
FROM clients
WHERE education NOT IN (1, 2, 3, 4)
GROUP BY education;

-- name: undocumented_marriage_codes
SELECT marriage, COUNT(*) AS n
FROM clients
WHERE marriage NOT IN (1, 2, 3)
GROUP BY marriage;

-- name: negative_bills
SELECT COUNT(*) AS n_clients_with_negative_bill
FROM clients
WHERE bill_amt1 < 0 OR bill_amt2 < 0 OR bill_amt3 < 0;

-- name: age_range
SELECT MIN(age) AS min_age, MAX(age) AS max_age FROM clients;
