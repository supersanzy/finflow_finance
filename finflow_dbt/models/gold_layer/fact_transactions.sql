
select  transaction_id,
        account_id
        transaction_reference,
        transaction_type,
        transaction_status,
        transaction_direction,
        amount,
        currency,
        transaction_channel,
        description,
        original_transaction_id,
        fee_for_transaction_id,
        transaction_at,
        created_at
from {{ ref('silver_transactions') }}
        