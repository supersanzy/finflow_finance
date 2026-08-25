with silver_transactions as 
(
    select transaction_id,
            account_id,
            transaction_reference,
            {{ clean_strings('transaction_type') }} as transaction_type,
            {{ clean_strings('transaction_status') }} as transaction_status,
            {{ clean_strings('transaction_direction') }} as transaction_direction,
            amount,
            case 
                when currency != 'NGN' then 'NGN'
                else currency
            end as currency,
            case 
                when len(transaction_channel) <= 4 THEN transaction_channel
                when transaction_channel is null then 'UNKNOWN TRANSACTION CHANNEL'
                else {{ clean_strings('transaction_channel') }} 
            end as transaction_channel,
            case 
                when description is null then 'UNKNOWN TRANSACTION DESCRIPTION'
                else description
            end as description,
            original_transaction_id,
            fee_for_transaction_id,
            transaction_at,
            created_at
    from {{ source('finflow_bronze_src', 'bronze_transactions') }}
),

    validated_transactions as
    (
        select *,
            count(*) over(partition by transaction_reference) as transaction_ref_rn
        from silver_transactions
    )

    select transaction_id, account_id, transaction_reference,
        transaction_type, transaction_status,
        transaction_direction, amount, currency, 
        transaction_channel, description, 
        original_transaction_id, fee_for_transaction_id,
        transaction_at, created_at
    from validated_transactions
    where amount > 0
    or transaction_at < created_at
    or transaction_ref_rn = 1