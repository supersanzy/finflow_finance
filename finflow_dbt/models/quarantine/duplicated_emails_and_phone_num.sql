
with duplicate_email_and_phone_number as
    (
        select *, count(*) over(partition by email) as email_rn,
                count(*) over(partition by phone_number order by customer_id) as phone_rn
        from {{ ref('silver_customers') }}

    )

    select *,
        case 
            when email_rn > 1 then 'duplicated_email'
            when phone_rn > 1 then 'duplicate_email_and_phone_number'
        end as data_quality_issue
        from duplicate_email_and_phone_number
    where email_rn > 1 or phone_rn > 1