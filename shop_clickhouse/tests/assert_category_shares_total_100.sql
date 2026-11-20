-- Category shares should add up to about 100 (rounding allowed).
select total_pct
from (select sum(revenue_share_pct) as total_pct from {{ ref('shopch_category_summary') }})
where abs(total_pct - 100) > 1
