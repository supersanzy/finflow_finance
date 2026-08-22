
{# Tests if the transaction_type is fee and if the fee for transaction reference id is null#}
select * from {{ ref('silver_transactions') }}
where transaction_type = 'Fee'
and fee_for_transaction_id is null