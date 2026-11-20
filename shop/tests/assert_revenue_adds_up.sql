-- The daily revenue table and the order table are two views of the same orders: their grand totals must agree.
select d.total as daily_total, o.total as orders_total
from (select sum(revenue) as total from {{ ref('shop_daily_revenue') }}) d
cross join (select sum(order_total) as total from {{ ref('fct_shop_orders') }} where is_revenue) o
where d.total <> o.total
