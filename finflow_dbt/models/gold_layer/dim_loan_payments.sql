select {{ dbt_utils.generate_surrogate_key(['loan_payment_id']) }} as loan_payment_key,
        loan_payment_id,
        loan_id,
        transaction_id,
        payment_reference,
        payment_amount,
        principal_amount,
        interest_amount,
        payment_status,
        payment_at,
        created_at
from {{ ref('silver_loan_payments') }}