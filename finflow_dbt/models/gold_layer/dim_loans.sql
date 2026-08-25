select 
        loan_id,
        customer_id,
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
        created_at
from {{ ref('silver_loans') }}