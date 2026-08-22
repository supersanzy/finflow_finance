with silver_accounts as 
(
    select account_id,
           customer_id, 
           account_number,
           {{ clean_strings('account_type') }} as account_type,
           case 
                when currency != 'NGN' then 'NGN' 
                else currency
            end as currency,
           balance,
           {{ clean_strings('account_status') }} as account_status,
           opened_at,
           closed_at
    from {{ source('finflow_bronze_src', 'bronze_accounts') }}
)

select * from silver_accounts
where balance > 0 
or closed_at > opened_at
or account_status = 'Closed' and closed_at is not null