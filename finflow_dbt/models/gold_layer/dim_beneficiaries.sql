select {{ dbt_utils.generate_surrogate_key(['beneficiary_id']) }} as beneficiary_key,
        beneficiary_id,
        customer_id,
        beneficiary_name,
        bank_name,
        status,
        created_at
from {{ ref('silver_beneficiaries') }}