with silver_loan_payments as
(
    select loan_payment_id,
            loan_id,
            transaction_id,
            payment_reference,
            payment_amount,
            principal_amount,
            interest_amount,
            {{ clean_strings('payment_status') }} as payment_status,
            payment_at,
            created_at
    from {{ source('finflow_bronze_src', 'bronze_loan_payments') }}
)

select * from silver_loan_payments