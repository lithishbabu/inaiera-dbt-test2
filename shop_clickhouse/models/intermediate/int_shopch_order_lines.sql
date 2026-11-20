-- One row per order line, with the product and the line total.
select
    i.order_item_id                                            as order_item_id,
    i.order_id                                                 as order_id,
    i.product_id                                               as product_id,
    p.product_name                                             as product_name,
    p.category                                                 as category,
    i.quantity                                                 as quantity,
    p.unit_price                                               as unit_price,
    cast(i.quantity * p.unit_price as Decimal(14, 2))          as line_total
from {{ ref('stg_shopch_order_items') }} as i
inner join {{ ref('stg_shopch_products') }} as p on p.product_id = i.product_id
