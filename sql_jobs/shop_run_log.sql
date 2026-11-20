-- SQL job for the Trino engine: adds ONE row to a log table on every run (it never deletes), so on a schedule it builds a history.
-- Run it a few times and watch the log grow. Trino has no transaction across statements: the first error stops the job.

create schema if not exists iceberg.shop_reports;

create table if not exists iceberg.shop_reports.run_log (
    logged_at   timestamp(6) with time zone,
    run_number  bigint,
    note        varchar
);

insert into iceberg.shop_reports.run_log
select
    cast(current_timestamp as timestamp(6) with time zone),
    coalesce((select max(run_number) from iceberg.shop_reports.run_log), 0) + 1,
    'sample run';

-- the latest five log rows, newest first
select * from iceberg.shop_reports.run_log order by logged_at desc limit 5;
