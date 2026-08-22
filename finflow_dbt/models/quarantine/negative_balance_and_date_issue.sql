

select
    *,
    case
        when closed_at < opened_at
            then 'closed_at_before_opened_at'

        when balance < 0
            then 'negative_balance'

        when account_status = 'CLOSED' and 
            closed_at IS NULL THEN 'no_account_closure_date'
    end as data_quality_issue,

    CURRENT_TIMESTAMP() as detected_at

from {{ ref('silver_accounts') }}

where closed_at < opened_at
or balance < 0
or account_status = 'CLOSED' and closed_at IS NULL  
