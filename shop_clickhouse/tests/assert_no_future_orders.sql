-- Fails if any order is dated in the future.
select order_id, order_date
from {{ ref('stg_shopch_orders') }}
where order_date > today()
