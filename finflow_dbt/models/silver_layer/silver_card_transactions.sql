with silver_card_transactions as
(
    select card_transaction_id,
            card_id,
            transaction_id,
            merchant_name,
            {{ clean_strings('merchant_category') }} as merchant_category,
            transaction_at,
            created_at
    from {{ source('finflow_bronze_src', 'bronze_card_transactions') }}
)

select * from silver_card_transactions