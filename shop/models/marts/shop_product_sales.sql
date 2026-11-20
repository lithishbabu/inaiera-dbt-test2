-- One row per product that sold: units, orders, revenue, and its rank by revenue.
select
    l.product_id,
    l.product_name,
    l.category,
    count(distinct l.order_id)                                         as orders,
    sum(l.quantity)                                                    as units_sold,
    cast(sum(l.line_total) as decimal(14, 2))                          as revenue,
    row_number() over (order by sum(l.line_total) desc)                as revenue_rank
from {{ ref('int_shop_order_lines') }} l
join {{ ref('fct_shop_orders') }} o on o.order_id = l.order_id
where o.is_revenue
group by l.product_id, l.product_name, l.category
