-- One row per product.
select
    product_id,
    product_name,
    category,
    cast(unit_price as Decimal(10, 2)) as unit_price
from {{ ref('shopch_products') }}
