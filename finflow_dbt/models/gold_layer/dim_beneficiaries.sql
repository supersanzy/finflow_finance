select 
        beneficiary_id,
        customer_id,
        beneficiary_name,
        bank_name,
        status,
        created_at
from {{ ref('silver_beneficiaries') }}