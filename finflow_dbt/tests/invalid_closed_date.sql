
select * 
from {{ ref('silver_accounts') }}
where opened_at > closed_at  
and account_status = 'Closed'