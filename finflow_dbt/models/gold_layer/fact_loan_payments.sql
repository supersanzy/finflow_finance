
select
    lp.loan_payment_id,
    lp.loan_id,
    l.account_id,
    l.customer_id,
    lp.transaction_id,
    lp.principal_amount,
    l.interest_rate,
    lp.interest_amount,
    l.total_repayable_amount,
    l.loan_status,
    lp.payment_status,
    lp.payment_at

from {{ ref('silver_loan_payments') }} as lp
join {{ ref('silver_loans') }} as l
    on lp.loan_id = l.loan_id
join {{ ref('silver_transactions') }} as t
    on t.transaction_id = lp.transaction_id
where t.transaction_type = 'Loan Payment'