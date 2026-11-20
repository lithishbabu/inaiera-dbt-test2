-- One row per order, with a normalised status.
select
    order_id,
    customer_id,
    order_date,
    lower(status) as status
from {{ ref('shop_orders') }}
