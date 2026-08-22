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
                when country != 'Nigeria' THEN 'Nigeria'
                else {{ clean_strings('country') }}      
            end as country, 
            {{ clean_strings('state') }} as state, 
            {{ clean_strings('city') }} as city,
            case 
                when address = '' then 'UNKNOWN ADDRESS'
                else {{ clean_strings('address') }}
            end as address, 
            {{ clean_strings('customer_status') }} as customer_status, 
            created_at,
            updated_at
    from {{ source('finflow_bronze_src', 'bronze_customers') }}
),

validated_customers as (

    select *,

        count(*) over (
            partition by email
        ) as email_count,

        count(*) over (
            partition by phone_number
        ) as phone_count

    from silver_customers

)

    select
        customer_id,
        first_name,
        last_name,
        email,
        phone_number,
        date_of_birth,
        gender,
        country,
        state,
        city,
        address,
        customer_status,
        created_at,
        updated_at

    from validated_customers
    where email_count = 1
    and phone_count = 1