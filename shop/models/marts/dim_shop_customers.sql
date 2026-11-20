-- One row per customer: lifetime value, first and last order, and a simple segment.
with revenue_orders as (
    select * from {{ ref('fct_shop_orders') }} where is_revenue
),
agg as (
    select
        customer_id,
        count(*)         as revenue_orders,
        min(order_date)  as first_order_date,
        max(order_date)  as last_order_date,
        sum(order_total) as lifetime_value
    from revenue_orders
    group by customer_id
)
select
    c.customer_id,
    c.full_name,
    c.email,
    c.city,
    c.signup_date,
    coalesce(a.revenue_orders, 0)                       as revenue_orders,
    a.first_order_date,
    a.last_order_date,
    cast(coalesce(a.lifetime_value, 0) as decimal(14, 2)) as lifetime_value,
    case
        when coalesce(a.lifetime_value, 0) >= 80000 then 'high'
        when coalesce(a.lifetime_value, 0) >= 20000 then 'medium'
        when coalesce(a.lifetime_value, 0) > 0      then 'low'
        else 'no_purchases'
    end as customer_segment
from {{ ref('stg_shop_customers') }} c
left join agg a on a.customer_id = c.customer_id
