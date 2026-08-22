select  {{ dbt_utils.generate_surrogate_key(['transfer_id']) }} as transfer_key,
        transfer_id,
        transfer_reference,
        sender_transaction_id,
        receiver_transaction_id,
        beneficiary_id,
        transfer_method,
        transfer_purpose,
        created_at
from {{ ref('silver_transfers') }}