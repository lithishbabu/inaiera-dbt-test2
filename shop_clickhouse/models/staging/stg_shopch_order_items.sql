-- One row per product line on an order.
select
    order_item_id,
    order_id,
    product_id,
    quantity
from {{ ref('shopch_order_items') }}
