{% test date_before_date(model, earlier_column, later_column) %}

    select *
    from {{ model }}
    where {{ earlier_column }} >= cast({{ later_column }} as date)

{% endtest %}