# inaiera-dbt-test2

A small, self-contained **Trino** dbt project: `shop/`.

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
