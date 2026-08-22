
select * from 
    {{ ref('silver_cards') }} 
where len(card_number) > 16