-- One row per customer, cleaned: a full name and a lower-case email.
select
    customer_id,
    first_name,
    last_name,
    concat(first_name, ' ', last_name) as full_name,
    lower(email)                       as email,
    city,
    signup_date
from {{ ref('shopch_customers') }}
