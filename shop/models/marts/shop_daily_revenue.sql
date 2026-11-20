-- Revenue per day (revenue orders only), with a running total (a Trino window function).
select
    order_date,
    count(*)                                              as orders,
    cast(sum(order_total) as decimal(14, 2))              as revenue,
    cast(round(avg(order_total), 2) as decimal(14, 2))    as avg_order_value,
    cast(sum(sum(order_total)) over (order by order_date) as decimal(14, 2)) as running_revenue
from {{ ref('fct_shop_orders') }}
where is_revenue
group by order_date
