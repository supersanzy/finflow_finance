with silver_beneficiaries as
(
    select beneficiary_id,
            customer_id,
            {{ clean_strings('beneficiary_name') }} as beneficiary_name,
            beneficiary_account,
            bank_name,
            {{ clean_strings('status') }} as status,
            created_at
    from {{ source('finflow_bronze_src', 'bronze_beneficiaries') }}
)

select * from silver_beneficiaries