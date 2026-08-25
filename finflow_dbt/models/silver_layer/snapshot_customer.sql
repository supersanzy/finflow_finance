
select customer_id,
        email,
        phone_number,
        state,
        city,
        address
from {{ ref('silver_customers')}}