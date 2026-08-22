with silver_customers as 
(
    select customer_id, 
            {{ clean_strings('first_name') }} as first_name, 
            {{ clean_strings('last_name') }} as last_name,
            email, 
            phone_number, 
            cast(date_of_birth as date) as date_of_birth,
            case
                when gender = 'FEMALEE' THEN 'Female'
                when gender = 'MALEE' THEN 'Male'
                else {{ clean_strings('gender') }}
            end as gender, 
            case 
                when country = 'NIG' THEN 'Nigeria'
                else {{ clean_strings('country') }}      
            end as country, 
            {{ clean_strings('state') }} as state, 
            {{ clean_strings('city') }} as city,
            {{ clean_strings('address') }} as address, 
            {{ clean_strings('customer_status') }} as customer_status, 
            created_at,
            updated_at
    from {{ source('finflow_bronze_src', 'bronze_customers') }}
)

select * from silver_customers