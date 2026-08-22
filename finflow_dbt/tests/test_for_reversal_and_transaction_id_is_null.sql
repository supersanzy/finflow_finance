select * from 
{{ ref('silver_transactions') }} 
where transaction_type = 'Reversal' 
and original_transaction_id is null