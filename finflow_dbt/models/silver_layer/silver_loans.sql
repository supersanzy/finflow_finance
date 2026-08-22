with silver_loans as
(
    select loan_id,
            customer_id,
            account_id,
            loan_reference,
            {{ clean_strings('loan_type') }} as loan_type,
            {{ clean_strings('loan_status') }} as loan_status,
            principal_amount,
            interest_rate,
            total_repayable_amount,
            outstanding_balance,
            term_months,
            approved_at,
            disbursed_at,
            maturity_date,
            created_at
    from {{ source('finflow_bronze_src', 'bronze_loans') }}
)

select * from silver_loans