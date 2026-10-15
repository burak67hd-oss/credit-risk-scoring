-- 04_features.sql
-- Feature engineering in SQL: one clean row per client, ready for the model.

DROP VIEW IF EXISTS client_features;

CREATE VIEW client_features AS
SELECT
    id,
    limit_bal,
    age,
    sex,
    -- Group undocumented codes into "others"
    CASE WHEN education IN (1, 2, 3) THEN education ELSE 4 END AS education,
    CASE WHEN marriage  IN (1, 2)    THEN marriage  ELSE 3 END AS marriage,

    -- Repayment behaviour
    pay_0                                                     AS last_status,
    CASE
        WHEN pay_0 <= -1 THEN 'paid_on_time'
        WHEN pay_0 = 0   THEN 'revolving'
        WHEN pay_0 = 1   THEN 'late_1m'
        WHEN pay_0 = 2   THEN 'late_2m'
        ELSE 'late_3m_plus'
    END                                                       AS last_status_group,
    MAX(pay_0, pay_2, pay_3, pay_4, pay_5, pay_6)             AS max_delay_6m,
    (pay_0 > 0) + (pay_2 > 0) + (pay_3 > 0)
      + (pay_4 > 0) + (pay_5 > 0) + (pay_6 > 0)               AS n_months_late_6m,

    -- Credit utilisation: share of the credit limit used on the last statement
    bill_amt1 / limit_bal                                     AS utilisation_last,
    (bill_amt1 + bill_amt2 + bill_amt3
      + bill_amt4 + bill_amt5 + bill_amt6) / 6.0 / limit_bal  AS utilisation_avg_6m,

    -- Payment ratio: how much of the bills the client actually paid over 6 months
    CASE
        WHEN (bill_amt1 + bill_amt2 + bill_amt3 + bill_amt4 + bill_amt5 + bill_amt6) <= 0 THEN 1.0
        ELSE MIN(1.0,
                 (pay_amt1 + pay_amt2 + pay_amt3 + pay_amt4 + pay_amt5 + pay_amt6) * 1.0
               / (bill_amt1 + bill_amt2 + bill_amt3 + bill_amt4 + bill_amt5 + bill_amt6))
    END                                                       AS payment_ratio_6m,

    pay_amt1                                                  AS last_payment,
    bill_amt1                                                 AS last_bill,

    default_next_month
FROM clients;
