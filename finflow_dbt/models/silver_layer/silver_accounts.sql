with silver_accounts as 
(
    select account_id,
           customer_id, 
           account_number,
           {{ clean_strings('account_type') }} as account_type,
           case 
                when currency = 'NIG' then 'NGN' 
                else currency
            end as currency,
           balance,
           {{ clean_strings('account_status') }} as account_status,
           opened_at,
           closed_at,
           case 
                when account_status = 'CLOSED' and 
                 closed_at IS NULL THEN 'No Account Closure Date'
            end as invalid_closed_at,
            case
                when opened_at > closed_at  
                and account_status = 'CLOSED' then TRUE
                else FALSE
            end as opened_at_date_grtr_than_closed_at_date,
            case
                when balance < 0 THEN TRUE
                else FALSE 
            end as balance_has_negative_values,
            case
                when currency != 'NGN' then TRUE
                else FALSE 
            end as currency_not_in_ngn
    from {{ source('finflow_bronze_src', 'bronze_accounts') }}
)

select * from silver_accounts