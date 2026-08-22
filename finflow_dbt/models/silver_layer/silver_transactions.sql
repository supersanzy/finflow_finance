with silver_transactions as 
(
    select transaction_id,
            account_id,
            transaction_reference,
            {{ clean_strings('transaction_type') }} as transaction_type,
            {{ clean_strings('transaction_status') }} as transaction_status,
            {{ clean_strings('transaction_direction') }} as transaction_direction,
            amount,
            currency,
            case 
                when len(transaction_channel) <= 4 THEN transaction_channel
                else {{ clean_strings('transaction_channel') }} 
            end as transaction_channel,
            description,
            original_transaction_id,
            fee_for_transaction_id,
            transaction_at,
            created_at,
            case
                when transaction_at > created_at then TRUE
                else FALSE
            end as transaction_date_grtr_than_created_date
    from {{ source('finflow_bronze_src', 'bronze_transactions') }}
)

select * from silver_transactions