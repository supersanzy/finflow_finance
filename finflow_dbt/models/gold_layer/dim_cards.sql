select 
        card_id,
        customer_id,
        account_id,
        card_number,
        card_type,
        card_status,
        issued_at,
        expires_at
from {{ref('silver_cards')}}