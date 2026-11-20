"""Python job for the Trino engine: checks that a Python job can really use Trino, one check at a time, and fails the run if any check fails.

It needs no data of its own (it creates and drops a scratch table), so it is the quickest way to tell a problem with the SERVER or the
connection apart from a problem with a project. Each check prints PASS or FAIL; the run fails (exit code 1) when any check fails.
Connection details come from the environment the Runner gives the job (INAIERA_TRINO_*); nothing is written in this file.
Packages come from requirements.txt in this folder.
"""
import os
import sys

import trino
from tabulate import tabulate

results = []


def record(name, ok, detail=""):
    results.append((name, "PASS" if ok else "FAIL", str(detail)[:80]))


engine = os.environ.get("INAIERA_ENGINE", "")
record("engine is trino", engine == "trino", engine or "not set")

needed = ["INAIERA_TRINO_HOST", "INAIERA_TRINO_PORT", "INAIERA_TRINO_CATALOG", "INAIERA_TRINO_HTTP_SCHEME"]
missing = [n for n in needed if not os.environ.get(n)]
record("Trino settings given to the job", not missing, "all present" if not missing else "missing: " + ", ".join(missing))

conn = None
if not missing:
    try:
        jwt = os.environ.get("INAIERA_TRINO_JWT")
        conn = trino.dbapi.connect(
            host=os.environ["INAIERA_TRINO_HOST"], port=int(os.environ["INAIERA_TRINO_PORT"]),
            http_scheme=os.environ["INAIERA_TRINO_HTTP_SCHEME"], catalog=os.environ["INAIERA_TRINO_CATALOG"],
            user=os.environ.get("INAIERA_TRINO_USER", "inaiera-python-job"),
            auth=trino.auth.JWTAuthentication(jwt) if jwt else None,
        )
        record("connect", True, f"{os.environ['INAIERA_TRINO_HOST']}:{os.environ['INAIERA_TRINO_PORT']}")
    except Exception as e:  # noqa: BLE001
        record("connect", False, e)


def check(name, fn):
    if conn is None:
        record(name, False, "no connection")
        return
    try:
        record(name, True, fn())
    except Exception as e:  # noqa: BLE001
        record(name, False, e)


def run(sql):
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def ddl(sql):
    """Run a statement that returns nothing useful; the check passes if it does not raise."""
    run(sql)
    return "ok"


def has_iceberg():
    if not any(row[0] == "iceberg" for row in run("show catalogs")):
        raise RuntimeError("no iceberg catalog")
    return "found"


check("run a query (select 1)", lambda: run("select 1")[0][0])
check("the iceberg catalog exists", has_iceberg)
check("create a schema", lambda: ddl("create schema if not exists iceberg.shop_reports"))
check("create a table", lambda: ddl("create table if not exists iceberg.shop_reports.connection_check (n integer)"))
check("write a row", lambda: ddl("insert into iceberg.shop_reports.connection_check values (1)"))
check("read it back", lambda: f"{run('select count(*) from iceberg.shop_reports.connection_check')[0][0]} rows")
check("drop the table", lambda: ddl("drop table if exists iceberg.shop_reports.connection_check"))
if conn is not None:
    conn.close()

print(tabulate(results, headers=["check", "result", "detail"]))
failed = [name for name, status, _ in results if status == "FAIL"]
print(f"{len(results)} checks: {len(results) - len(failed)} passed, {len(failed)} failed")
if failed:
    sys.exit("connection check FAILED: " + ", ".join(failed))
