{#- True when an order status counts toward revenue (driven by the var revenue_statuses). -#}
{% macro is_revenue_status(column_name) %}
    ({{ column_name }} in (
        {%- for s in var('revenue_statuses') -%}
            '{{ s }}'{{ ", " if not loop.last }}
        {%- endfor -%}
    ))
{% endmacro %}
