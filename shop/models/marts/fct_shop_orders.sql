-- One row per order with its totals and a revenue flag.
select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    count(l.order_item_id)                                              as line_count,
    sum(l.quantity)                                                     as units,
    cast(sum(l.line_total) as decimal(14, 2))                           as order_total,
    {{ is_revenue_status('o.status') }}                                 as is_revenue,
    array_join(array_sort(array_distinct(array_agg(l.category))), ', ') as categories   -- Trino array functions
from {{ ref('stg_shop_orders') }} o
join {{ ref('int_shop_order_lines') }} l on l.order_id = o.order_id
group by o.order_id, o.customer_id, o.order_date, o.status
