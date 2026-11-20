-- One row per category, with its share of total revenue.
select
    category,
    count(*)                                                              as products_sold,
    sum(units_sold)                                                       as units_sold,
    cast(sum(revenue) as decimal(14, 2))                                  as revenue,
    cast(round(100.0 * sum(revenue) / sum(sum(revenue)) over (), 1) as decimal(5, 1)) as revenue_share_pct
from {{ ref('shop_product_sales') }}
group by category
