
select tr.transfer_id,
        tr.transfer_reference,
        tr.sender_transaction_id,
        tr.receiver_transaction_id,
        tr.beneficiary_id,
        str.account_id as sender_account_id,
        str.amount as transfer_amount,
        str.transaction_at
from {{ ref('silver_transfers') }} as tr
left join {{ ref('silver_transactions') }} as str
on tr.sender_transaction_id = str.transaction_id
where str.transaction_type = 'Transfer'