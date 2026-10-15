-- 01_schema.sql
-- Raw table: one row per credit card client (Taiwan, April–September 2005).
-- Source: UCI Machine Learning Repository, "Default of Credit Card Clients" (Yeh & Lien, 2009).

DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    id            INTEGER PRIMARY KEY,
    limit_bal     REAL    NOT NULL,   -- credit limit (NT dollars)
    sex           INTEGER NOT NULL,   -- 1 = male, 2 = female
    education     INTEGER NOT NULL,   -- 1 = graduate school, 2 = university, 3 = high school, 4 = others (0, 5, 6 undocumented)
    marriage      INTEGER NOT NULL,   -- 1 = married, 2 = single, 3 = others (0 undocumented)
    age           INTEGER NOT NULL,
    -- Repayment status, from most recent (pay_0 = September) to oldest (pay_6 = April)
    -- -2 = no consumption, -1 = paid in full, 0 = revolving credit, 1..9 = months of payment delay
    pay_0 INTEGER, pay_2 INTEGER, pay_3 INTEGER, pay_4 INTEGER, pay_5 INTEGER, pay_6 INTEGER,
    -- Bill statement amounts (September -> April)
    bill_amt1 REAL, bill_amt2 REAL, bill_amt3 REAL, bill_amt4 REAL, bill_amt5 REAL, bill_amt6 REAL,
    -- Amounts paid (September -> April)
    pay_amt1 REAL, pay_amt2 REAL, pay_amt3 REAL, pay_amt4 REAL, pay_amt5 REAL, pay_amt6 REAL,
    default_next_month INTEGER NOT NULL  -- target: 1 = default in October 2005
);
