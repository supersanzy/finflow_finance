select 
        account_id,
        customer_id,
        account_type,
        account_status,
        opened_at,
        closed_at
from {{ ref('silver_accounts') }}