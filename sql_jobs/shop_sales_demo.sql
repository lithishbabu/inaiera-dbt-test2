-- SQL job for the Trino engine: builds a small sales report from sample data written right here (no other project or table needed).
-- Statements run one after another. Trino has no transaction across statements: the first error stops the job and what ran
-- before it stays done. Comments like these are ignored.

create schema if not exists iceberg.shop_reports;

drop table if exists iceberg.shop_reports.sales_by_city;

-- 1. sample orders, written inline with VALUES, summed per city
create table iceberg.shop_reports.sales_by_city as
with orders (order_id, city, amount) as (
    values
        (1, 'Hyderabad', cast(1200.00 as decimal(12, 2))),
        (2, 'Hyderabad', cast(800.50 as decimal(12, 2))),
        (3, 'Mumbai',    cast(2500.00 as decimal(12, 2))),
        (4, 'Mumbai',    cast(1750.25 as decimal(12, 2))),
        (5, 'Chennai',   cast(640.00 as decimal(12, 2))),
        (6, 'Delhi',     cast(3100.00 as decimal(12, 2))),
        (7, 'Delhi',     cast(900.00 as decimal(12, 2))),
        (8, 'Delhi',     cast(450.75 as decimal(12, 2)))
)
select
    city,
    count(*)                                                       as orders,
    cast(sum(amount) as decimal(14, 2))                            as revenue,
    cast(round(100.0 * sum(amount) / sum(sum(amount)) over (), 1) as decimal(5, 1)) as revenue_share_pct,
    cast(current_timestamp as timestamp(6) with time zone)         as refreshed_at
from orders
group by city;

-- 2. the report, biggest city first (the last statement's rows show in the run's steps)
select city, orders, revenue, revenue_share_pct
from iceberg.shop_reports.sales_by_city
order by revenue desc;
