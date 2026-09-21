select 
        account_id,
        customer_key,
        account_number,
        account_type,
        account_status,
        opened_at,
        closed_at
from {{ ref('silver_accounts') }} as a
join {{ ref('dim_customers') }} as c
on a.customer_id = c.customer_id