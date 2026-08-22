
select * 
from {{ ref('silver_loans') }} 
where principal_amount > total_repayable_amount
or approved_at > disbursed_at