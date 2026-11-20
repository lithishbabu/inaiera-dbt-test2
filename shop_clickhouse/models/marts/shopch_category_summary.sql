{{ config(order_by='category') }}
-- One row per category, with its share of total revenue.
-- Two steps on purpose: in ClickHouse an output column called `revenue` would shadow the source column of the same name inside the
-- same query, so the totals are summed first and the share is worked out from them.
with by_category as (
    select
        category,
        count()                               as products_sold,
        sum(units_sold)                       as units_sold,
        sum(revenue)                          as category_revenue
    from {{ ref('shopch_product_sales') }}
    group by category
)
select
    category,
    products_sold,
    units_sold,
    cast(category_revenue as Decimal(14, 2))                                               as revenue,
    cast(round(100.0 * category_revenue / sum(category_revenue) over (), 1) as Decimal(5, 1)) as revenue_share_pct
from by_category
