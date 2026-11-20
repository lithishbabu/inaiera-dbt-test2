-- Fails if any order is dated in the future.
select order_id, order_date
from {{ ref('stg_shop_orders') }}
where order_date > current_date
