


with duplicate_transaction_reference as
(
    select *, 
        count(*) over(partition by transaction_reference) as transaction_ref_rn
    from {{ ref('silver_transactions') }}
)

select *,
    case 
        when amount < 0 then 'negative_balance'
        when transaction_at > created_at then 'transaction_at_before_created_at'
        when transaction_ref_rn > 1 then 'duplicated_transaction_reference'
    end as data_quality_issues
    from duplicate_transaction_reference
where transaction_ref_rn > 1
or amount < 0
or transaction_at > created_at
