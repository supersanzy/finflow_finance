{% macro clean_strings(column_name) %}
    initcap(trim(replace({{column_name}}, '_', ' ')))
{% endmacro %}