with silver_cards as
(
    select card_id,
            customer_id,
            account_id,
            card_number,
            {{ clean_strings('card_type') }} as card_type,
            {{ clean_strings('card_status') }} as card_status,
            issued_at,
            expires_at

    from {{ source('finflow_bronze_src', 'bronze_cards') }}
)

select * from silver_cards