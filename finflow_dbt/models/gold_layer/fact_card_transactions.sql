
select ct.card_transaction_id,
        ct.card_id,
        ct.transaction_id,
        c.customer_id,
        c.account_id as sender_account_id,
        t.transaction_at
from {{ ref('silver_card_transactions') }} as ct
join {{ ref('silver_cards')}} as c
on ct.card_id = c.card_id
join {{ ref('silver_transactions') }} as t
on t.transaction_id = ct.transaction_id
where t.transaction_type = 'Card Payment'