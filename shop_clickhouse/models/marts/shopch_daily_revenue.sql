{{ config(order_by='order_date') }}
-- Revenue per day (revenue orders only), with a running total (a ClickHouse window function).
select
    order_date,
    count()                                                     as orders,
    cast(sum(order_total) as Decimal(14, 2))                    as revenue,
    cast(round(avg(order_total), 2) as Decimal(14, 2))          as avg_order_value,
    cast(sum(sum(order_total)) over (order by order_date) as Decimal(14, 2)) as running_revenue
from {{ ref('fct_shopch_orders') }}
where is_revenue
group by order_date
