"""Python job for the Trino engine: builds iceberg.shop_reports.sales_by_product from sample data written in this script, then prints it.

Needs no other project or table. How a job gets its engine: the Runner puts the Trino connection into the environment of the run
(INAIERA_TRINO_HOST / _PORT / _CATALOG / _HTTP_SCHEME, and INAIERA_TRINO_JWT, or INAIERA_TRINO_USER on a Trino without login).
Never write a host or a password in code. Packages come from requirements.txt in this folder, installed fresh for every run.
"""
import os
import sys

import trino
from tabulate import tabulate

if os.environ.get("INAIERA_ENGINE") != "trino":
    sys.exit(f"This job runs on the Trino engine (this run uses '{os.environ.get('INAIERA_ENGINE', '')}'). Register it with engine Trino.")

print(f"run {os.environ.get('INAIERA_RUN_ID', '')[:8]} on commit {os.environ.get('INAIERA_GIT_SHA', '')[:8]}")

jwt = os.environ.get("INAIERA_TRINO_JWT")
conn = trino.dbapi.connect(
    host=os.environ["INAIERA_TRINO_HOST"],
    port=int(os.environ["INAIERA_TRINO_PORT"]),
    http_scheme=os.environ["INAIERA_TRINO_HTTP_SCHEME"],
    catalog=os.environ["INAIERA_TRINO_CATALOG"],
    user=os.environ.get("INAIERA_TRINO_USER", "inaiera-python-job"),
    auth=trino.auth.JWTAuthentication(jwt) if jwt else None,
)
cur = conn.cursor()


def run(sql):
    """Run one statement; Trino runs it as its result is read, so always read it."""
    cur.execute(sql)
    return cur.fetchall()


try:
    run("create schema if not exists iceberg.shop_reports")
    run("drop table if exists iceberg.shop_reports.sales_by_product")
    run("""
        create table iceberg.shop_reports.sales_by_product as
        with sales (product, category, units, unit_price) as (
            values
                ('Laptop 14 inch',      'computers',   3, cast(58000.00 as decimal(10, 2))),
                ('Wireless Mouse',      'accessories', 9, cast(899.00 as decimal(10, 2))),
                ('Mechanical Keyboard', 'accessories', 5, cast(3499.00 as decimal(10, 2))),
                ('27in Monitor',        'displays',    4, cast(16500.00 as decimal(10, 2))),
                ('Standing Desk',       'furniture',   2, cast(24500.00 as decimal(10, 2)))
        )
        select product, category, units,
               cast(units * unit_price as decimal(14, 2))                              as revenue,
               row_number() over (order by units * unit_price desc)                    as revenue_rank,
               cast(current_timestamp as timestamp(6) with time zone)                  as refreshed_at
        from sales
    """)
    rows = run("select revenue_rank, product, category, units, revenue from iceberg.shop_reports.sales_by_product order by revenue_rank")
finally:
    conn.close()

print(tabulate(rows, headers=["rank", "product", "category", "units", "revenue"]))
print(f"wrote {len(rows)} rows to iceberg.shop_reports.sales_by_product")
