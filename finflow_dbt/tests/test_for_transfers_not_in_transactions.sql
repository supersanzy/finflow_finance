SELECT tr.*
FROM transfers AS tr
LEFT JOIN transactions AS sender_tt
    ON tr.sender_transaction_id = sender_tt.transaction_id
LEFT JOIN transactions AS receiver_tt
    ON tr.receiver_transaction_id = receiver_tt.transaction_id
WHERE sender_tt.transaction_id IS NULL