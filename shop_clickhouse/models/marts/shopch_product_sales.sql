{{ config(order_by='product_id') }}
-- One row per product that sold: units, orders, revenue, and its rank by revenue.
select
    l.product_id                                                       as product_id,
    l.product_name                                                     as product_name,
    l.category                                                         as category,
    uniqExact(l.order_id)                                              as orders,
    sum(l.quantity)                                                    as units_sold,
    cast(sum(l.line_total) as Decimal(14, 2))                          as revenue,
    row_number() over (order by sum(l.line_total) desc)                as revenue_rank
from {{ ref('int_shopch_order_lines') }} as l
inner join {{ ref('fct_shopch_orders') }} as o on o.order_id = l.order_id
where o.is_revenue
group by l.product_id, l.product_name, l.category
