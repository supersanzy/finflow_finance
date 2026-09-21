select 
        loan_id,
        customer_key,
        account_id,
        loan_reference,
        loan_type,
        loan_status,
        principal_amount,
        interest_rate,
        total_repayable_amount,
        outstanding_balance,
        term_months,
        approved_at,
        disbursed_at,
        maturity_date,
        s.created_at
from {{ ref('silver_loans') }} as s
join {{ ref('dim_customers')}} as c
on c.customer_id = s.customer_id