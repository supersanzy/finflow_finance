{# Transaction_at timestamp entry is not supposed to be greater than created_at timestamp #}
{# This test checks whether transaction_id timestamp is greater than created_at #}

select * from {{ ref('silver_transactions') }}
where transaction_at > created_at