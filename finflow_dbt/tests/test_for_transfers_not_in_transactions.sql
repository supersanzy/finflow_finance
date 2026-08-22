SELECT tr.*
FROM {{ ref('silver_transfers') }} AS tr
LEFT JOIN {{ ref('silver_transactions') }} AS sender_tt
    ON tr.sender_transaction_id = sender_tt.transaction_id
LEFT JOIN {{ ref('silver_transactions') }} AS receiver_tt
    ON tr.receiver_transaction_id = receiver_tt.transaction_id
WHERE sender_tt.transaction_id IS NULL