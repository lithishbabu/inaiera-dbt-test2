{{ config(order_by='customer_id') }}
-- One row per customer: lifetime value, first and last order, and a simple segment.
-- join_use_nulls: ClickHouse fills a missing left-join match with 0 / an empty value unless told to use NULL.
with revenue_orders as (
    select * from {{ ref('fct_shopch_orders') }} where is_revenue
),
agg as (
    select
        customer_id,
        count()         as revenue_orders,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        sum(order_total) as lifetime_value
    from revenue_orders
    group by customer_id
)
select
    c.customer_id                                              as customer_id,
    c.full_name                                                as full_name,
    c.email                                                    as email,
    c.city                                                     as city,
    c.signup_date                                              as signup_date,
    coalesce(a.revenue_orders, 0)                              as revenue_orders,
    a.first_order_date                                         as first_order_date,
    a.last_order_date                                          as last_order_date,
    cast(coalesce(a.lifetime_value, 0) as Decimal(14, 2))      as lifetime_value,
    multiIf(
        coalesce(a.lifetime_value, 0) >= 80000, 'high',
        coalesce(a.lifetime_value, 0) >= 20000, 'medium',
        coalesce(a.lifetime_value, 0) > 0,      'low',
        'no_purchases'
    )                                                          as customer_segment
from {{ ref('stg_shopch_customers') }} as c
left join agg as a on a.customer_id = c.customer_id
settings join_use_nulls = 1
