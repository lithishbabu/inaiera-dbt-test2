{{ config(order_by='order_id') }}
-- One row per order with its totals and a revenue flag.
select
    o.order_id                                                          as order_id,
    o.customer_id                                                       as customer_id,
    o.order_date                                                        as order_date,
    o.status                                                            as status,
    count(l.order_item_id)                                              as line_count,
    sum(l.quantity)                                                     as units,
    cast(sum(l.line_total) as Decimal(14, 2))                           as order_total,
    {{ is_revenue_status('o.status') }}                                 as is_revenue,
    arrayStringConcat(arraySort(arrayDistinct(groupArray(l.category))), ', ') as categories   -- ClickHouse array functions
from {{ ref('stg_shopch_orders') }} as o
inner join {{ ref('int_shopch_order_lines') }} as l on l.order_id = o.order_id
group by o.order_id, o.customer_id, o.order_date, o.status
