select *
from {{ ref('silver_cards') }}
where card_status = 'Inactive'
and expires_at > CURRENT_DATE