"""Python job for the Trino engine: PRINTS what the Runner's Trino really is, so nobody has to guess. It changes nothing (read-only).

It prints: the catalog the Runner writes to, every Trino catalog with the connector behind it (iceberg, postgresql, hive, ...), the
schemas in the Runner's catalog, and the tables of the 'public' schema (where the dbt `shop` project builds). A catalog whose connector is
`postgresql` means those tables really live in PostgreSQL; `iceberg` means files in the warehouse (S3 / MinIO / disk).
Connection details come from the environment the Runner gives the job (INAIERA_TRINO_*). Packages come from requirements.txt here.
"""
import os
import sys

import trino
from tabulate import tabulate

catalog = os.environ.get("INAIERA_TRINO_CATALOG", "")
print(f"Runner writes to Trino catalog: {catalog or '(not set)'}")
print(f"Trino: {os.environ.get('INAIERA_TRINO_HOST')}:{os.environ.get('INAIERA_TRINO_PORT')}  ({os.environ.get('INAIERA_TRINO_HTTP_SCHEME')})\n")

jwt = os.environ.get("INAIERA_TRINO_JWT")
conn = trino.dbapi.connect(
    host=os.environ["INAIERA_TRINO_HOST"], port=int(os.environ["INAIERA_TRINO_PORT"]),
    http_scheme=os.environ["INAIERA_TRINO_HTTP_SCHEME"], catalog=catalog,
    user=os.environ.get("INAIERA_TRINO_USER", "inaiera-python-job"),
    auth=trino.auth.JWTAuthentication(jwt) if jwt else None,
)


def show(title, sql):
    print(title)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        head = [d[0] for d in cur.description]
        print(tabulate(rows, headers=head, tablefmt="simple") if rows else "(nothing)")
    except Exception as e:  # noqa: BLE001
        print(f"could not read: {str(e)[:300]}")
    print()


# connector_name is the real engine behind each catalog.
show("1. Catalogs and the connector behind each one", "select catalog_name, connector_name from system.metadata.catalogs order by 1")
show(f"2. Schemas in '{catalog}'", f'show schemas from "{catalog}"')
show(f"3. Tables in {catalog}.public (the dbt shop project builds here)", f'show tables from "{catalog}".public')
show("4. First rows of dim_shop_customers (proves the table is readable through Trino)",f'select * from "{catalog}"."public"."dim_shop_customers" limit 3')
sys.exit(0)
