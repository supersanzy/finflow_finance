with silver_transfers as 
(
    select transfer_id,
            transfer_reference,
            sender_transaction_id,
            receiver_transaction_id,
            beneficiary_id,
            case 
                when transfer_method = 'BANK_TRANSFER' THEN 'Bank Transfer'
                when transfer_method = 'INTERNAL_TRANSFER' and 
                receiver_transaction_id IS NULL then 'Bank Transfer'
            end as transfer_method,
            transfer_purpose,
            created_at
    from {{ source('finflow_bronze_src', 'bronze_transfers') }}
    
)

select * from silver_transfers
