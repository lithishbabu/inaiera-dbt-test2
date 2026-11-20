# inaiera-dbt-test2

Two small, self-contained dbt projects, one per engine. Neither depends on the other or on any other project:

- `shop/` runs on **Trino**.
- `shop_clickhouse/` runs on **ClickHouse** (see the end of this file).

## shop (Trino)

It loads its own sample data (four CSV seeds: customers, products, orders, order items) and builds everything from it, so it **does not depend on any other project** and can run at any time. Every table and view is prefixed `shop` so it never clashes with another project writing into the same Trino schema.

| Layer | Objects |
| --- | --- |
| Seeds | `shop_customers`, `shop_products`, `shop_orders`, `shop_order_items` |
| Staging (views) | `stg_shop_customers`, `stg_shop_products`, `stg_shop_orders`, `stg_shop_order_items` |
| Intermediate (view) | `int_shop_order_lines` |
| Marts (tables) | `fct_shop_orders`, `dim_shop_customers`, `shop_daily_revenue`, `shop_product_sales`, `shop_category_summary` |

20 data tests run with the build (unique, not null, accepted values, relationships, positive values, plus three custom checks).

## Run it
Register it in the Workspace under **Jobs → dbt → Register project**:

- Git repository URL: `https://github.com/lithishbabu/inaiera-dbt-test2.git`
- Project name: `shop`
- Branch: `main`
- Engine: `Trino`

Then press **Run now**. A run builds 4 seeds, 10 models and 20 tests (34 steps), all passing.

## shop_clickhouse (ClickHouse)

The same shop data and the same kind of models, written in ClickHouse SQL (`concat`, `multiIf`, `groupArray`, `uniqExact`, window functions, `MergeTree` tables with an `order_by`). It has its own four CSV seeds, and every object is prefixed `shopch`. In ClickHouse a dbt "schema" is a database, so the models land in the database the Runner is configured with.

| Layer | Objects |
| --- | --- |
| Seeds | `shopch_customers`, `shopch_products`, `shopch_orders`, `shopch_order_items` |
| Staging (views) | `stg_shopch_customers`, `stg_shopch_products`, `stg_shopch_orders`, `stg_shopch_order_items` |
| Intermediate (view) | `int_shopch_order_lines` |
| Marts (tables) | `fct_shopch_orders`, `dim_shopch_customers`, `shopch_daily_revenue`, `shopch_product_sales`, `shopch_category_summary` |

19 data tests run with the build.

Register it under **Jobs -> dbt -> Register project**: Git repository URL `https://github.com/lithishbabu/inaiera-dbt-test2.git`, Project name `shop_clickhouse`, Branch `main`, Engine `ClickHouse`. A run builds 4 seeds, 10 models and 19 tests (33 steps), all passing.
