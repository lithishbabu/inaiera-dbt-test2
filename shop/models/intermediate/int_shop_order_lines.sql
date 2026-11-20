-- One row per order line, with the product and the line total.
select
    i.order_item_id,
    i.order_id,
    i.product_id,
    p.product_name,
    p.category,
    i.quantity,
    p.unit_price,
    cast(i.quantity * p.unit_price as decimal(14, 2)) as line_total
from {{ ref('stg_shop_order_items') }} i
join {{ ref('stg_shop_products') }} p on p.product_id = i.product_id
