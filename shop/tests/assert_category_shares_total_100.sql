-- Category shares should add up to about 100 (rounding allowed).
select sum(revenue_share_pct) as total_pct
from {{ ref('shop_category_summary') }}
having abs(sum(revenue_share_pct) - 100) > 1
