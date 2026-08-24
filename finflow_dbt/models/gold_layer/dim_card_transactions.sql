select {{ dbt_utils.generate_surrogate_key(['card_transaction_id']) }} as card_transaction_key,
        card_transaction_id,
        card_id,
        transaction_id,
        merchant_name,
        merchant_category,
        transaction_at,
        created_at
from {{ ref('silver_card_transactions') }}