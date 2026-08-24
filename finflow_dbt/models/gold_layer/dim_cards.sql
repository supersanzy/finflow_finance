select {{ dbt_utils.generate_surrogate_key(['card_id']) }} as card_key,
        card_id,
        account_id,
        card_type,
        card_status,
        issued_at,
        expires_at
from {{ref('silver_cards')}}